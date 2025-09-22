# # import jwt
# import datetime
# import secrets
# import os
# import hashlib
# from typing import Dict, Any
# from dataclasses import dataclass
# from urllib.parse import urlencode
# from binascii import hexlify, unhexlify


# @dataclass
# class Claim:
#     token: str
#     user_id: str
#     role: str


# class JWTTokenManager:
#     def __init__(
#         self,
#         secret_key: str,
#         algorithm: str = "HS256",
#         token_expiry_hours: int = 24,
#     ):

#         if getattr(self, "_initialized", False):
#             return
#         if not all([secret_key]):
#             raise ValueError("JWT Must provide secret_key")
#         # Use provided secret key or generate a secure one
#         self.secret_key = secret_key or secrets.token_urlsafe(64)
#         self.algorithm = algorithm
#         self.token_expiry_hours = token_expiry_hours
#         self._initialized = True

#     def generate_claim(
#         self, user_id: str, role: str, additional_claims: Dict[str, Any] = None
#     ) -> Claim:
#         """
#         Generate a JWT claim with standard and custom claims

#         Args:
#             user_id: Unique user identifier
#             role: User role (e.g., 'admin', 'user', 'moderator')
#             additional_claims: Additional custom claims to include

#         Returns:
#             Claim object containing the token and user information
#         """
#         # Standard claims
#         payload = {
#             "sub": user_id,  # Subject (user ID)
#             "role": role,  # Custom claim for role
#             "iat": datetime.datetime.now(),
#             "exp": datetime.datetime.now()
#             + datetime.timedelta(hours=self.token_expiry_hours),  # Expiration
#         }

#         # Add additional custom claims if provided
#         if additional_claims:
#             payload.update(additional_claims)

#         # Generate JWT token
#         token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

#         return Claim(token=token, user_id=user_id, role=role)

#     def verify_token(self, token: str) -> Dict[str, Any]:
#         """
#         Verify and decode a JWT token

#         Args:
#             token: JWT token string

#         Returns:
#             Decoded payload if valid

#         Raises:
#             jwt.ExpiredSignatureError: Token has expired
#             jwt.InvalidTokenError: Token is invalid
#         """
#         try:
#             payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
#             return payload
#         except jwt.ExpiredSignatureError:
#             raise Exception("Token has expired")
#         except jwt.InvalidTokenError:
#             raise Exception("Invalid token")

#     def refresh_token(self, token: str) -> Claim:
#         """
#         Refresh an existing token (extend expiration)

#         Args:
#             token: Existing JWT token

#         Returns:
#             New Claim object with refreshed token
#         """
#         # Verify and get current payload
#         payload = self.verify_token(token)

#         # Create new token with extended expiration
#         payload["exp"] = datetime.datetime.now() + datetime.timedelta(
#             hours=self.token_expiry_hours
#         )
#         payload["iat"] = datetime.datetime.now()

#         new_token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

#         return Claim(token=new_token, user_id=payload["sub"], role=payload["role"])


# def hash_password(password):
#     # Generate a unique random salt for each password (16 bytes = 128 bits)
#     salt = secrets.token_bytes(16)

#     # Hash the password with the salt using PBKDF2 with SHA256
#     hashed_password = hashlib.pbkdf2_hmac(
#         "sha256",
#         password.encode("utf-8"),
#         salt,
#         100000,  # 100,000 iterations (OWASP recommendation)
#         dklen=32,  # 32 bytes = 256 bits
#     )

#     # Combine salt and hash for storage: format = salt(hex) + hash(hex)
#     salt_hex = hexlify(salt).decode("utf-8")
#     hash_hex = hexlify(hashed_password).decode("utf-8")
#     stored_password = f"{salt_hex}:{hash_hex}"

#     return stored_password


# def verify_password(stored_password: str, provided_password: str):
#     try:
#         # Split the stored value into salt and hash components
#         salt_hex, hash_hex = stored_password.split(":")
#         salt = unhexlify(salt_hex)
#         stored_hash = unhexlify(hash_hex)

#         # Hash the provided password with the same salt
#         provided_hash = hashlib.pbkdf2_hmac(
#             "sha256", provided_password.encode("utf-8"), salt, 100000, dklen=32
#         )

#         # Compare securely using constant-time comparison
#         return hashlib.compare_digest(provided_hash, stored_hash)

#     except (ValueError, TypeError):
#         # Handle invalid stored password format
#         return False
