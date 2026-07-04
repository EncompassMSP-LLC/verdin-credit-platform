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
