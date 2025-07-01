# Implementation Plan: Enhanced SSH Key Configuration (Refined)

**Objective:** Implement the features for specifying SSH keys directly in the configuration file, as detailed in the updated `context/tasks/ssh-key-specifications.md`.

This plan outlines the necessary changes to the codebase, including file modifications, logic updates, and documentation, reflecting the refined requirements.

---

## 1. Update Configuration Data Structure

**File to Modify:** `pei_docker/user_config.py`

**(Completed)** The `SshUser` dataclass has been extended with `pubkey_text`, `privkey_file`, and `privkey_text`, and validation logic has been added. No further changes are needed here.

---

## 2. Update Configuration Template

**File to Modify:** `pei_docker/templates/base-image-gen.yml`

**(Completed)** The template has been updated to document the new fields and provide examples. No further changes are needed here.

---

## 3. Process New Configuration in Core Logic

**File to Modify:** `pei_docker/config_processor.py`

**(Completed)** The core logic has been updated to process the new SSH fields and pass them as build arguments. No further changes are needed here.

---

## 4. Update SSH Setup Script (Refined Logic)

**File to Modify:** `pei_docker/project_files/installation/stage-1/internals/setup-ssh.sh`

**Changes:**

1.  **Initialize `authorized_keys`:** Before adding any keys, create an empty `authorized_keys` file to ensure a clean state.
2.  **Handle Private Key and Generate Public Key:**
    *   If `privkey_text` or `privkey_file` is provided, save the private key to `~/.ssh/id_rsa`.
    *   **Generate the corresponding public key** from the private key using `ssh-keygen -y -f ~/.ssh/id_rsa`.
    *   If no private key is provided, generate a new key pair as before.
3.  **Append All Public Keys:**
    *   Append the generated public key (from the provided or newly created private key) to `authorized_keys`.
    *   Append the public key from `pubkey_file` to `authorized_keys`, if it exists.
    *   Append the public key from `pubkey_text` to `authorized_keys`, if it exists.
    *   This ensures that all specified public keys are authorized, as they may not be a pair.
4.  **Set Permissions:** Ensure correct, secure permissions are set for all created files (`.ssh` directory, `id_rsa`, and `authorized_keys`).

---

## 5. Testing Strategy

1.  **Create a Test Configuration:** Create a new example file, e.g., `pei_docker/examples/ssh-with-unpaired-keys.yml`, to test the new functionality.
2.  **Define Test Cases:**
    *   **Valid:** Provide a `privkey_text` and a *different*, unpaired `pubkey_text`.
    *   **Valid:** Provide a `privkey_file` and a *different*, unpaired `pubkey_file`.
    *   **Verify:** SSH into the container using the provided private key.
    *   **Verify:** Check the `authorized_keys` file inside the container to confirm that it contains **both** the public key generated from the private key and the separately provided public key.
3.  **Execute and Verify:**
    *   Run the `configure` and `build` commands for the test case.
    *   Perform the verification steps to confirm the implementation is correct.
