Function Get-PetstorePet {
    [cmdletbinding()]
    param(
        [Parameter(Mandatory, ValueFromPipeline)]
        [int]$Id
    )
    Begin{}
    Process{
        $RestMethodParams =@{
            Uri = "https://petstore.swagger.io/v2/pet/$Id"
            ContentType = "application/json"
            Method = "GET"
        }
        Invoke-RestMethod @RestMethodParams
    }
    End{}
}



