$AccountName = "cosmosdb-2-sc"
$DatabaseName = "db1"
$token=Get-AzAccessToken -ResourceUrl "https://$AccountName.documents.azure.com"
$restUri="https://$AccountName.documents.azure.com:443/dbs/$DatabaseName/colls/CapabilityManagement.Capability/docs"
$dateTime = [DateTime]::UtcNow.ToString("r")
$keyType="aad"
$tokenVersion="1.0"
$cosmosAuthHeader=[System.Web.HttpUtility]::UrlEncode("type=$keyType&ver=$tokenVersion&sig=$($token.Token)")
write-host("cosmosAuthHeader:`n`n$cosmosAuthHeader`n`n")

$env:cosmosAuthHeader = $cosmosAuthHeader