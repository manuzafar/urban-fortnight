"""
Email notification utility for Seedcraft.

Sends alerts to the founder when packs are generated.
Uses Resend API for email delivery.
"""

import httpx
import structlog

from config import settings

logger = structlog.get_logger(__name__)


async def send_founder_alert(
    user_email: str,
    product_idea: str,
    session_id: str,
    product_name: str | None = None,
) -> bool:
    """
    Send email alert to founder when a pack is generated.

    Args:
        user_email: Email of the user who generated the pack.
        product_idea: The product idea text (truncated if too long).
        session_id: The session ID for the pack.
        product_name: Optional product name from the generated pack.

    Returns:
        bool: True if email was sent successfully, False otherwise.
    """
    # If no API key configured, just log
    if not settings.resend_api_key:
        logger.info(
            "founder_alert_skipped",
            reason="no_api_key",
            user_email=user_email,
            product_idea=product_idea[:50],
            session_id=session_id,
        )
        return False

    if not settings.founder_email:
        logger.info(
            "founder_alert_skipped",
            reason="no_founder_email",
            user_email=user_email,
        )
        return False

    try:
        # Truncate product idea for subject
        idea_preview = product_idea[:50].replace("\n", " ")
        if len(product_idea) > 50:
            idea_preview += "..."

        subject = f"New pack: {product_name or idea_preview}"

        # Build pack URL
        pack_url = f"{settings.frontend_url}/session/{session_id}"

        html_content = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px 30px; border-radius: 8px 8px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 20px;">New Inception Pack Generated</h1>
            </div>

            <div style="background: #f8f9fa; padding: 30px; border: 1px solid #e9ecef; border-top: none; border-radius: 0 0 8px 8px;">
                <p style="margin: 0 0 20px; color: #495057; font-size: 15px;">
                    <strong>User:</strong> {user_email}
                </p>

                {f'<p style="margin: 0 0 20px; color: #495057; font-size: 15px;"><strong>Product Name:</strong> {product_name}</p>' if product_name else ''}

                <p style="margin: 0 0 20px; color: #495057; font-size: 15px;">
                    <strong>Product Idea:</strong><br>
                    <span style="color: #6c757d;">{product_idea[:500]}{'...' if len(product_idea) > 500 else ''}</span>
                </p>

                <p style="margin: 0 0 20px; color: #495057; font-size: 15px;">
                    <strong>Session ID:</strong> {session_id[:8]}...
                </p>

                <a href="{pack_url}"
                   style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                          color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none;
                          font-weight: 600; font-size: 14px;">
                    View Pack
                </a>

                <hr style="border: none; border-top: 1px solid #e9ecef; margin: 30px 0;">

                <p style="margin: 0; color: #6c757d; font-size: 13px;">
                    Follow up with this user for feedback!
                </p>
            </div>
        </div>
        """

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {settings.resend_api_key}"},
                json={
                    "from": f"Seedcraft <{settings.email_from_address}>",
                    "to": settings.founder_email,
                    "subject": subject,
                    "html": html_content,
                },
            )

            if response.status_code in (200, 201):
                logger.info(
                    "founder_alert_sent",
                    user_email=user_email,
                    session_id=session_id,
                )
                return True
            else:
                logger.error(
                    "founder_alert_failed",
                    status_code=response.status_code,
                    response=response.text,
                    user_email=user_email,
                    session_id=session_id,
                )
                return False

    except Exception as e:
        logger.error(
            "founder_alert_error",
            error=str(e),
            user_email=user_email,
            session_id=session_id,
            exc_info=True,
        )
        return False


async def get_user_email_from_supabase(user_id: str) -> str | None:
    """
    Get user email from Supabase.

    Args:
        user_id: The Supabase user ID.

    Returns:
        The user's email address, or None if not found.
    """
    try:
        from supabase import create_client

        supabase = create_client(settings.supabase_url, settings.supabase_service_key)
        result = supabase.auth.admin.get_user_by_id(user_id)

        if result and result.user and result.user.email:
            return result.user.email

        return None
    except Exception as e:
        logger.error(
            "get_user_email_failed",
            user_id=user_id,
            error=str(e),
        )
        return None
