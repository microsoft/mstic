param(
    [string]$ConfigFile # Optional: User-provided config file
)

# Fetch Microsoft-identified publicly disclosed MachineKeys.txt
$DisclosedKeysUrl = "https://github.com/microsoft/mstic/blob/master/RapidReleaseTI/MachineKeys.csv"

try {
    $DisclosedKeys = Invoke-WebRequest -Uri $DisclosedKeysUrl -ErrorAction Stop
    if (-not $DisclosedKeys -or -not $DisclosedKeys.Content) {
        Write-Host -ForegroundColor Yellow "Error: Downloaded content from $DisclosedKeysUrl is empty."
        exit 1
    }
    Write-Host -ForegroundColor Green "DisclosedKeys loaded successfully."
} catch {
    Write-Host -ForegroundColor Red "Error downloading MachineKeys.txt: $_"
    exit 1
}

# Load the WebAdministration module
Import-Module WebAdministration

# Define the method allowing to check the machineKey element for known disclosed key values
function Check-MachineKey {
    param (
        [string]$webConfigFilePathEnv,
        [string]$hashedKeyContents,
        [int]$tabCount
    )

    $tabs = "`t" * $tabCount
    write-host "${tabs}Checking $webConfigFilePathEnv"
    [xml]$webConfig = Get-Content $webConfigFilePathEnv

    # Check if the machineKey element exists and check if either the validationKey or decryptionKey is public
    if ($webConfig.configuration.'system.web'.machineKey) 
    {            
        $machineKey = $webConfig.configuration.'system.web'.machineKey
        $validationKey = $machineKey.validationKey
        $decryptionKey = $machineKey.decryptionKey   
        if ($validationKey) {
            $hashValidationKey = [BitConverter]::ToString([System.Security.Cryptography.SHA256]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes($validationKey))) -replace "-", ""
            if ($hashedKeyContents -match $hashValidationKey) {
                Write-Host -ForegroundColor Red "${tabs}!!!WARNING!!!: validationKey $validationKey - is publicly disclosed!"
            }
        }

        if ($decryptionKey) {
            $hashDecryptionKey = [BitConverter]::ToString([System.Security.Cryptography.SHA256]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes($decryptionKey))) -replace "-", ""
            if ($hashedKeyContents -match $hashDecryptionKey) {
                Write-Host -ForegroundColor Red "${tabs}!!!WARNING!!!: decryptionKey $decryptionKey  - is publicly disclosed!"
            }
        }                       
    } 
}


# Define the method to check for web applications inside a site
function Check-WebApplications {
    param (
        [string]$siteName,
        [string]$hashedKeyContents
    )

    $webApps = Get-WebApplication -Site $siteName
    $webAppCount = $webApps.Count
    write-host -ForegroundColor Cyan "`tFound $webAppCount web application(s)"
    if ($webAppCount -gt 0) {
        foreach ($webApp in $webApps) {
            write-host "`tName: $($webApp.Path), Root Folder: $($webApp.PhysicalPath)"
            $webConfigFiles = Get-ChildItem -Path "$($webApp.PhysicalPath)" -Recurse -Filter "web.config"
            foreach ($webConfigFile in $webConfigFiles) {
                $webConfigFilePath = $webConfigFile.FullName
                $webConfigFilePathEnv = [Environment]::ExpandEnvironmentVariables($webConfigFilePath)
                Check-MachineKey -webConfigFilePathEnv $webConfigFilePathEnv -hashedKeyContents $hashedKeyContents -tabCount 2
            }
        }
    }
}

# Define the method to check for virtual directories inside a site
function Check-VirtualDirectories {
    param (
        [string]$siteName,
        [string]$hashedKeyContents
    )

    $virtualDirs = Get-WebVirtualDirectory -Site $siteName
    $virtualDirCount = $virtualDirs.Count
    write-host -ForegroundColor Cyan "`tFound $virtualDirCount virtual directory(ies)"
    if ($virtualDirCount -gt 0) {
        foreach ($virtualDir in $virtualDirs) {
            write-host "`tName: $($virtualDir.Path), Root Folder: $($virtualDir.PhysicalPath)"
            $webConfigFiles = Get-ChildItem -Path "$($virtualDir.PhysicalPath)" -Recurse -Filter "web.config"
            foreach ($webConfigFile in $webConfigFiles) {
                $webConfigFilePath = $webConfigFile.FullName
                $webConfigFilePathEnv = [Environment]::ExpandEnvironmentVariables($webConfigFilePath)
                Check-MachineKey -webConfigFilePathEnv $webConfigFilePathEnv -hashedKeyContents $hashedKeyContents -tabCount 2
            }
        }
    }
}


# Method to process a web.config file
function Check-WebConfigFile {
    param([string]$WebConfigFilePath,
          [string]$hashedKeyContents)

    try {
        [xml]$WebConfig = Get-Content -Path $WebConfigFilePath -ErrorAction Stop
    } catch {
        Write-Host -ForegroundColor Yellow "Error: Unable to read $WebConfigFilePath. Skipping."
        return
    }

    # invoke the code to check the file directly
    Check-MachineKey -webConfigFilePathEnv $WebConfigFilePath -hashedKeyContents $hashedKeyContents -tabCount 1
}

# If user provides a config file, process only that file
if ($ConfigFile) {
    if (-not (Test-Path $ConfigFile)) {
        Write-Host -ForegroundColor Red "Error: Specified config file '$ConfigFile' does not exist."
        exit 1
    }
    Write-Host "Checking user-provided config file: $ConfigFile"
    Check-WebConfigFile -WebConfigFilePath $ConfigFile -hashedKeyContents $DisclosedKeys.Content
    exit 0
}


# Get list of IIS sites
$sites=Get-ChildItem IIS:\Sites
# Iterate through each website
foreach ($site in $sites) 
{
   write-host -ForegroundColor DarkYellow "***** Site: $($site.Name)"
   $physicalPath =  [Environment]::ExpandEnvironmentVariables($site.PhysicalPath)    
   $webConfigFiles = Get-ChildItem -Path "$physicalPath" -Recurse -Filter "web.config"
   # Iterate web.config files for each site
   
   foreach ($webConfigFile in $webConfigFiles) {
        # Load the XML content of the web.config file        
        $webConfigFilePath=$webConfigFile.FullName
        $webConfigFilePathEnv=[Environment]::ExpandEnvironmentVariables($webConfigFilePath)
       
        Check-MachineKey -webConfigFilePathEnv $webConfigFilePathEnv -hashedKeyContents $DisclosedKeys.Content -tabCount 1

    }

    # Check for all web applications inside a site
    Check-WebApplications -siteName $site.Name -hashedKeyContents $DisclosedKeys.Content

    # Check for all virtual directories inside a site
    Check-VirtualDirectories -siteName $site.Name -hashedKeyContents $DisclosedKeys.Content
}
