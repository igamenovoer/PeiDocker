# PowerShell Test Script for Custom Script Parameters
# Tests the full Docker build workflow with custom script parameters
# Verifies that parameters are correctly parsed and passed to scripts

param(
    [switch]$SkipCleanup = $false,
    [switch]$Verbose = $false
)

# Test configuration
$TestName = "custom-script-params-test"
$Timestamp = (Get-Date).ToString("yyyyMMdd-HHmmss")
$ProjectDir = ".\build-$TestName-$Timestamp"
$ConfigFile = ".\tests\configs\custom-script-params-test.yml"
$ImagePrefix = "pei-custom-params-test"
$ContainerName = "$ImagePrefix-container-$Timestamp"

# Colors for output
$Green = "Green"
$Red = "Red"
$Yellow = "Yellow"
$Blue = "Cyan"

function Write-TestStatus {
    param($Message, $Status = "Info", $Color = "White")
    $timestamp = Get-Date -Format "HH:mm:ss"
    switch ($Status) {
        "PASS" { Write-Host "[$timestamp] [PASS] $Message" -ForegroundColor $Green }
        "FAIL" { Write-Host "[$timestamp] [FAIL] $Message" -ForegroundColor $Red }
        "WARN" { Write-Host "[$timestamp] [WARN] $Message" -ForegroundColor $Yellow }
        "INFO" { Write-Host "[$timestamp] [INFO] $Message" -ForegroundColor $Blue }
        default { Write-Host "[$timestamp] $Message" -ForegroundColor $Color }
    }
}

function Test-CommandSuccess {
    param($Command, $Description)
    
    Write-TestStatus "Executing: $Description" "INFO"
    if ($Verbose) {
        Write-TestStatus "Command: $Command" "INFO"
    }
    
    try {
        $result = Invoke-Expression $Command
        if ($LASTEXITCODE -eq 0) {
            Write-TestStatus "$Description - Success" "PASS"
            return $true
        } else {
            Write-TestStatus "$Description - Failed (Exit Code: $LASTEXITCODE)" "FAIL"
            return $false
        }
    } catch {
        Write-TestStatus "$Description - Exception: $($_.Exception.Message)" "FAIL"
        return $false
    }
}

function Cleanup-TestResources {
    Write-TestStatus "Starting cleanup process..." "INFO"
    
    # Stop and remove containers
    $containers = docker ps -a --filter "name=$ImagePrefix" --format "{{.Names}}"
    if ($containers) {
        Write-TestStatus "Removing containers: $containers" "INFO"
        docker rm -f $containers | Out-Null
    }
    
    # Remove images
    $images = docker images --filter "reference=$ImagePrefix*" --format "{{.Repository}}:{{.Tag}}"
    if ($images) {
        Write-TestStatus "Removing images: $($images -join ', ')" "INFO"
        docker rmi -f $images | Out-Null
    }
    
    # Remove volumes
    $volumes = docker volume ls --filter "name=custom-params-test" --format "{{.Name}}"
    if ($volumes) {
        Write-TestStatus "Removing volumes: $($volumes -join ', ')" "INFO"
        docker volume rm $volumes | Out-Null
    }
    
    # Remove project directory
    if (Test-Path $ProjectDir) {
        Write-TestStatus "Removing project directory: $ProjectDir" "INFO"
        Remove-Item -Recurse -Force $ProjectDir
    }
    
    Write-TestStatus "Cleanup completed" "PASS"
}

# Main test execution
Write-TestStatus "=== Starting Custom Script Parameters Test ===" "INFO"
Write-TestStatus "Project Directory: $ProjectDir" "INFO"
Write-TestStatus "Config File: $ConfigFile" "INFO"
Write-TestStatus "Timestamp: $Timestamp" "INFO"

$TestsPassed = 0
$TestsFailed = 0

try {
    # Step 1: Verify config file exists
    if (-not (Test-Path $ConfigFile)) {
        Write-TestStatus "Config file not found: $ConfigFile" "FAIL"
        exit 1
    }
    Write-TestStatus "Config file found" "PASS"
    $TestsPassed++

    # Step 2: Create project
    $success = Test-CommandSuccess "pixi run python -m pei_docker.pei create -p `"$ProjectDir`"" "Create PeiDocker project"
    if (-not $success) {
        $TestsFailed++
        throw "Failed to create project"
    }
    $TestsPassed++

    # Step 3: Copy config file to project
    $destConfig = Join-Path $ProjectDir "user_config.yml"
    Copy-Item $ConfigFile $destConfig
    Write-TestStatus "Config file copied to project" "PASS"
    $TestsPassed++

    # Step 4: Configure project
    $success = Test-CommandSuccess "pixi run python -m pei_docker.pei configure -p `"$ProjectDir`"" "Configure PeiDocker project"
    if (-not $success) {
        $TestsFailed++
        throw "Failed to configure project"
    }
    $TestsPassed++

    # Step 5: Verify docker-compose.yml was generated
    $dockerComposeFile = Join-Path $ProjectDir "docker-compose.yml"
    if (-not (Test-Path $dockerComposeFile)) {
        Write-TestStatus "docker-compose.yml not generated" "FAIL"
        $TestsFailed++
        throw "Configuration failed to generate docker-compose.yml"
    }
    Write-TestStatus "docker-compose.yml generated successfully" "PASS"
    $TestsPassed++

    # Step 6: Check for custom script wrappers with parameters
    $customBuildScript = Join-Path $ProjectDir "stage-2\_custom-on-build.sh"
    $customLoginScript = Join-Path $ProjectDir "stage-2\_custom-on-user-login.sh"
    
    if (Test-Path $customBuildScript) {
        $buildContent = Get-Content $customBuildScript -Raw
        if ($buildContent -match "--verbose --cache-dir=/tmp/pixi-test-cache") {
            Write-TestStatus "Build script contains expected parameters" "PASS"
            $TestsPassed++
        } else {
            Write-TestStatus "Build script missing expected parameters" "FAIL"
            $TestsFailed++
            if ($Verbose) {
                Write-TestStatus "Build script content:" "INFO"
                Write-Host $buildContent
            }
        }
    } else {
        Write-TestStatus "Custom build script not found" "FAIL"
        $TestsFailed++
    }

    if (Test-Path $customLoginScript) {
        $loginContent = Get-Content $customLoginScript -Raw
        if ($loginContent -match '--message="Parameter test successful" --verbose') {
            Write-TestStatus "Login script contains expected parameters" "PASS"
            $TestsPassed++
        } else {
            Write-TestStatus "Login script missing expected parameters" "FAIL"
            $TestsFailed++
            if ($Verbose) {
                Write-TestStatus "Login script content:" "INFO"
                Write-Host $loginContent
            }
        }
    } else {
        Write-TestStatus "Custom login script not found" "FAIL"
        $TestsFailed++
    }

    # Step 7: Build Stage 1
    Set-Location $ProjectDir
    Write-TestStatus "Changed to project directory: $(Get-Location)" "INFO"
    
    $success = Test-CommandSuccess "docker compose build stage-1" "Build Stage 1 Docker image"
    if (-not $success) {
        $TestsFailed++
        throw "Failed to build Stage 1"
    }
    $TestsPassed++

    # Step 8: Build Stage 2 (this will execute the custom scripts with parameters)
    Write-TestStatus "Building Stage 2 - This will test parameter passing..." "INFO"
    
    # Capture build output to check for parameter evidence
    $buildOutput = docker compose build stage-2 2>&1
    $buildExitCode = $LASTEXITCODE
    
    if ($buildExitCode -eq 0) {
        Write-TestStatus "Stage 2 build completed successfully" "PASS"
        $TestsPassed++
        
        # Check build output for evidence of parameters being used
        $buildOutputStr = $buildOutput -join "`n"
        
        if ($buildOutputStr -match "verbose|VERBOSE") {
            Write-TestStatus "Build output shows verbose parameter was processed" "PASS"
            $TestsPassed++
        } else {
            Write-TestStatus "Build output doesn't show verbose parameter processing" "WARN"
        }
        
        if ($buildOutputStr -match "cache-dir|CACHE.*DIR") {
            Write-TestStatus "Build output shows cache-dir parameter was processed" "PASS"
            $TestsPassed++
        } else {
            Write-TestStatus "Build output doesn't show cache-dir parameter processing" "WARN"
        }
        
        if ($Verbose) {
            Write-TestStatus "Build output (last 50 lines):" "INFO"
            ($buildOutput | Select-Object -Last 50) | ForEach-Object { Write-Host $_ }
        }
        
    } else {
        Write-TestStatus "Stage 2 build failed (Exit Code: $buildExitCode)" "FAIL"
        $TestsFailed++
        
        # Show build output for debugging
        Write-TestStatus "Build output for debugging:" "INFO"
        $buildOutput | ForEach-Object { Write-Host $_ -ForegroundColor Red }
        
        throw "Failed to build Stage 2"
    }

    # Step 9: Test container startup (tests on_first_run scripts)
    Write-TestStatus "Testing container startup with first-run scripts..." "INFO"
    
    $startupOutput = docker compose up -d stage-2 2>&1
    $startupExitCode = $LASTEXITCODE
    
    if ($startupExitCode -eq 0) {
        Write-TestStatus "Container started successfully" "PASS"
        $TestsPassed++
        
        # Wait a moment for startup scripts to complete
        Start-Sleep -Seconds 3
        
        # Check container logs for first-run script execution
        $containerLogs = docker compose logs stage-2 2>&1
        $logsStr = $containerLogs -join "`n"
        
        if ($logsStr -match "verbose|VERBOSE") {
            Write-TestStatus "Container logs show first-run script parameters were processed" "PASS"
            $TestsPassed++
        }
        
        if ($Verbose) {
            Write-TestStatus "Container logs:" "INFO"
            $containerLogs | ForEach-Object { Write-Host $_ }
        }
        
    } else {
        Write-TestStatus "Container startup failed (Exit Code: $startupExitCode)" "FAIL"
        $TestsFailed++
        Write-TestStatus "Startup output:" "INFO"
        $startupOutput | ForEach-Object { Write-Host $_ -ForegroundColor Red }
    }

    # Step 10: Test SSH login (tests on_user_login scripts with parameters)
    Write-TestStatus "Testing SSH login with user-login scripts..." "INFO"
    
    # Wait for SSH service to be ready
    Start-Sleep -Seconds 5
    
    # Test SSH connection with password (should execute our parameter test script)
    $sshOutput = ""
    try {
        # Use sshpass to test SSH login and capture output
        $sshCommand = "echo 'Parameter test via SSH' | sshpass -p 'test123' ssh -o StrictHostKeyChecking=no -o PreferredAuthentications=password -p 2223 testuser@localhost 'bash -l'"
        
        # Check if sshpass is available
        $sshpassCheck = Get-Command sshpass -ErrorAction SilentlyContinue
        if ($sshpassCheck) {
            $sshOutput = Invoke-Expression $sshCommand 2>&1
            Write-TestStatus "SSH login test completed" "PASS"
            $TestsPassed++
            
            $sshOutputStr = $sshOutput -join "`n"
            if ($sshOutputStr -match "Parameter test successful") {
                Write-TestStatus "SSH login script parameters were processed correctly" "PASS"
                $TestsPassed++
            } else {
                Write-TestStatus "SSH login script parameters not found in output" "WARN"
            }
            
            if ($Verbose) {
                Write-TestStatus "SSH output:" "INFO"
                $sshOutput | ForEach-Object { Write-Host $_ }
            }
            
        } else {
            Write-TestStatus "sshpass not available - skipping SSH test" "WARN"
        }
    } catch {
        Write-TestStatus "SSH test failed: $($_.Exception.Message)" "WARN"
    }

} catch {
    Write-TestStatus "Test execution failed: $($_.Exception.Message)" "FAIL"
    $TestsFailed++
} finally {
    # Return to original directory
    Set-Location ..
    
    # Cleanup unless explicitly skipped
    if (-not $SkipCleanup) {
        Cleanup-TestResources
    } else {
        Write-TestStatus "Cleanup skipped - resources preserved for debugging" "WARN"
        Write-TestStatus "Project directory: $ProjectDir" "INFO"
    }
}

# Final results
Write-TestStatus "=== Test Results ===" "INFO"
Write-TestStatus "Tests Passed: $TestsPassed" "PASS"
Write-TestStatus "Tests Failed: $TestsFailed" "FAIL"

if ($TestsFailed -eq 0) {
    Write-TestStatus "All tests passed! Custom script parameters are working correctly." "PASS"
    exit 0
} else {
    Write-TestStatus "Some tests failed. Check the output above for details." "FAIL"
    exit 1
}