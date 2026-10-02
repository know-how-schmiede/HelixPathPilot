"""Best-effort cleanup without losing the original operation failure."""

from ..i18n import tr


def cleanup_created(entities, original_error):
    """Delete owned objects in reverse order, then report any cleanup failures.

    If cleanup succeeds, return so the caller can re-raise the original error.
    Never stop trying later objects because one deletion fails.
    """
    failures = []
    for label, entity in reversed(entities):
        try:
            if entity.deleteMe() is False:
                failures.append(tr('{p0}: deletion failed', p0=label))
        except Exception as error:
            failures.append(f'{label}: {error}')
    if failures:
        raise RuntimeError(tr('{p0} Cleanup incomplete: ', p0=original_error)
                           + '; '.join(failures)) from original_error
