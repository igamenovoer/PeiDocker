#!/usr/bin/env python3
"""
Debug script to test SSH key generation directly.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from pei_docker.pei_utils import generate_public_key_from_private

def test_key_generation():
    """Test key generation with the generated test key"""
    
    # Test key from our earlier generation
    test_private_key = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAACmFlczI1Ni1jdHIAAAAGYmNyeXB0AAAAGAAAABCe4n/pzj
LqP51FHF1ur+LnAAAAGAAAAAEAAAAzAAAAC3NzaC1lZDI1NTE5AAAAIGWeLKDDqOiNnk2H
c8DIBsfHVFU+YaSvkDwti4Snjf/gAAAAoFSGY+hUy35Nf/go6bwlXRs+NZab2+CiRviT3N
ft8Kj5JnLSa1W+n4RsYTTByJLnUeRGceOVl2642VlqrMbbPZQrNAijXDOknu2chRKCxCXa
32XYSOrWj11a0lddago9vRavgiLkj8TaRNmP4YTCa6pigZDM78dH++v59fBaCtLPAmvFEI
xwpwYINA7QdCdqJ66PVnzzpE/v0h+eASFrTcY=
-----END OPENSSH PRIVATE KEY-----"""
    
    print("Testing SSH key generation...")
    print(f"Private key length: {len(test_private_key)}")
    print(f"Starts with: {test_private_key[:50]}...")
    print(f"Ends with: ...{test_private_key[-50:]}")
    
    try:
        public_key = generate_public_key_from_private(test_private_key)
        print(f"✓ Successfully generated public key:")
        print(f"  {public_key}")
        return True
    except Exception as e:
        print(f"✗ Failed to generate public key: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_key_generation()
    sys.exit(0 if success else 1)
