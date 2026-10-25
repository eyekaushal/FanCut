// FanCut on Azure: two Container Apps (api, web) in one environment, with a registry,
// Log Analytics and Application Insights. Hostnames are wired here, never typed by hand:
// the API's own hostname goes into its MCP allow-list and the web app's URL into CORS.
//
// The Foundry model deployment and Azure AI Speech already exist (created in the
// Foundry portal); their endpoint, deployment name and keys come in as parameters
// and are stored as Container Apps secrets.
targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the azd environment; used to name resources.')
param environmentName string

@minLength(1)
@description('Azure region for every resource.')
param location string

@description('Foundry: the Azure OpenAI endpoint of the resource, e.g. https://<name>.openai.azure.com/')
param llmEndpoint string = ''

@description('Foundry: the model deployment name, e.g. gpt-4.1-mini-1')
param llmDeployment string = ''

@secure()
@description('Foundry: the resource API key. Empty keeps the deterministic templates speaking.')
param llmApiKey string = ''

@description('Azure AI Speech region, e.g. westus3')
param speechRegion string = ''

@secure()
@description('Azure AI Speech key. Empty hides the voice switch.')
param speechKey string = ''

var tags = { 'azd-env-name': environmentName }
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))

resource rg 'Microsoft.Resources/resourceGroups@2024-11-01' = {
  name: 'rg-${environmentName}'
  location: location
  tags: tags
}

module resources 'resources.bicep' = {
  name: 'resources'
  scope: rg
  params: {
    location: location
    tags: tags
    resourceToken: resourceToken
    llmEndpoint: llmEndpoint
    llmDeployment: llmDeployment
    llmApiKey: llmApiKey
    speechRegion: speechRegion
    speechKey: speechKey
  }
}

// azd reads these back into the environment after `azd provision`.
output AZURE_LOCATION string = location
output AZURE_RESOURCE_GROUP string = rg.name
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = resources.outputs.registryLoginServer
output API_URL string = resources.outputs.apiUrl
output WEB_URL string = resources.outputs.webUrl
output APPLICATIONINSIGHTS_NAME string = resources.outputs.appInsightsName
