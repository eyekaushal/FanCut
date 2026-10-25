// Everything inside the resource group. The two apps are created with a placeholder
// image; `azd deploy` builds the real images, pushes them to the registry and swaps
// them in (it finds each app by its `azd-service-name` tag).
param location string
param tags object
param resourceToken string
param llmEndpoint string
param llmDeployment string
@secure()
param llmApiKey string
param speechRegion string
@secure()
param speechKey string

var apiName = 'ca-api-${resourceToken}'
var webName = 'ca-web-${resourceToken}'
var placeholderImage = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

// -- Monitoring ----------------------------------------------------------------------

resource logs 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'log-${resourceToken}'
  location: location
  tags: tags
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi-${resourceToken}'
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logs.id
  }
}

// -- Registry and the identity that pulls from it -----------------------------------

resource registry 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' = {
  name: 'crfancut${resourceToken}'
  location: location
  tags: tags
  sku: { name: 'Basic' }
  properties: {
    adminUserEnabled: false
  }
}

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-${resourceToken}'
  location: location
  tags: tags
}

// AcrPull, so the apps pull images with the identity rather than a password.
var acrPullRole = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
resource acrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(registry.id, identity.id, acrPullRole)
  scope: registry
  properties: {
    roleDefinitionId: acrPullRole
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// -- Container Apps environment ------------------------------------------------------

resource env 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'cae-${resourceToken}'
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logs.properties.customerId
        sharedKey: logs.listKeys().primarySharedKey
      }
    }
  }
}

// Hostnames follow from the app names and the environment's domain, so both apps can
// be told about each other in this same deployment.
var apiHost = '${apiName}.${env.properties.defaultDomain}'
var webHost = '${webName}.${env.properties.defaultDomain}'
var apiUrl = 'https://${apiHost}'
var webUrl = 'https://${webHost}'

// -- The API -------------------------------------------------------------------------

var llmConfigured = !empty(llmEndpoint) && !empty(llmDeployment) && !empty(llmApiKey)
var speechConfigured = !empty(speechRegion) && !empty(speechKey)

resource api 'Microsoft.App/containerApps@2024-03-01' = {
  name: apiName
  location: location
  tags: union(tags, { 'azd-service-name': 'api' })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${identity.id}': {} }
  }
  properties: {
    managedEnvironmentId: env.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
        allowInsecure: false
      }
      registries: [
        {
          server: registry.properties.loginServer
          identity: identity.id
        }
      ]
      secrets: concat(
        [{ name: 'appinsights-connection-string', value: appInsights.properties.ConnectionString }],
        llmConfigured ? [{ name: 'llm-api-key', value: llmApiKey }] : [],
        speechConfigured ? [{ name: 'speech-key', value: speechKey }] : []
      )
    }
    template: {
      containers: [
        {
          name: 'api'
          image: placeholderImage
          resources: { cpu: json('1.0'), memory: '2Gi' }
          env: concat(
            [
              { name: 'NK_ENVIRONMENT', value: 'production' }
              { name: 'NK_HOST', value: '0.0.0.0' }
              { name: 'NK_PORT', value: '8000' }
              { name: 'NK_CORS_ORIGINS', value: '["${webUrl}"]' }
              { name: 'NK_MCP_ALLOWED_HOSTS', value: '["${apiHost}"]' }
              { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', secretRef: 'appinsights-connection-string' }
              { name: 'OTEL_SERVICE_NAME', value: 'fancut-api' }
            ],
            llmConfigured
              ? [
                  { name: 'NK_LLM_ENDPOINT', value: llmEndpoint }
                  { name: 'NK_LLM_DEPLOYMENT', value: llmDeployment }
                  { name: 'NK_LLM_API_KEY', secretRef: 'llm-api-key' }
                ]
              : [],
            speechConfigured
              ? [
                  { name: 'NK_SPEECH_REGION', value: speechRegion }
                  { name: 'NK_SPEECH_KEY', secretRef: 'speech-key' }
                ]
              : []
          )
          probes: [
            {
              type: 'Liveness'
              httpGet: { path: '/health', port: 8000 }
              initialDelaySeconds: 15
              periodSeconds: 30
            }
            {
              type: 'Readiness'
              httpGet: { path: '/health', port: 8000 }
              initialDelaySeconds: 5
              periodSeconds: 10
            }
          ]
        }
      ]
      // One replica, always on: channels live in memory, and a live stream must not
      // land on a different instance than the one that created the channel.
      scale: { minReplicas: 1, maxReplicas: 1 }
    }
  }
  dependsOn: [acrPull]
}

// -- The web app ---------------------------------------------------------------------

resource web 'Microsoft.App/containerApps@2024-03-01' = {
  name: webName
  location: location
  tags: union(tags, { 'azd-service-name': 'web' })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${identity.id}': {} }
  }
  properties: {
    managedEnvironmentId: env.id
    configuration: {
      ingress: {
        external: true
        targetPort: 3000
        transport: 'http'
        allowInsecure: false
      }
      registries: [
        {
          server: registry.properties.loginServer
          identity: identity.id
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'web'
          image: placeholderImage
          resources: { cpu: json('0.5'), memory: '1Gi' }
          env: [
            { name: 'PORT', value: '3000' }
            { name: 'HOSTNAME', value: '0.0.0.0' }
          ]
        }
      ]
      scale: { minReplicas: 1, maxReplicas: 2 }
    }
  }
  dependsOn: [acrPull]
}

output registryLoginServer string = registry.properties.loginServer
output apiUrl string = apiUrl
output webUrl string = webUrl
output appInsightsName string = appInsights.name
