"""SCIM provisioning feature gate dependencies."""

from fastapi import HTTPException, status

from api.core.feature_flags import FeatureFlag, is_feature_enabled


def require_scim_provisioning_enabled() -> None:
    if not is_feature_enabled(FeatureFlag.ENABLE_ENTERPRISE):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enterprise features are not enabled",
        )
    if not is_feature_enabled(FeatureFlag.ENABLE_SCIM_PROVISIONING):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SCIM provisioning is not enabled",
        )


def require_idp_federation_enabled() -> None:
    if not is_feature_enabled(FeatureFlag.ENABLE_ENTERPRISE):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enterprise features are not enabled",
        )
    if not is_feature_enabled(FeatureFlag.ENABLE_IDP_FEDERATION):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IdP federation is not enabled",
        )


def require_saml_federation_metadata_enabled() -> None:
    require_idp_federation_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_SAML_FEDERATION_METADATA):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SAML federation metadata upload is not enabled",
        )


def require_hris_bidirectional_sync_enabled() -> None:
    require_saml_federation_metadata_enabled()
    if not is_feature_enabled(FeatureFlag.ENABLE_HRIS_BIDIRECTIONAL_SYNC):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="HRIS bidirectional sync is not enabled",
        )
