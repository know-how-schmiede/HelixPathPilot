"""Best-effort cleanup without losing the original operation failure."""


def cleanup_created(entities, original_error):
    """Delete owned objects in reverse order, then report any cleanup failures.

    If cleanup succeeds, return so the caller can re-raise the original error.
    Never stop trying later objects because one deletion fails.
    """
    failures = []
    for label, entity in reversed(entities):
        try:
            if entity.deleteMe() is False:
                failures.append(f'{label}: Löschen fehlgeschlagen')
        except Exception as error:
            failures.append(f'{label}: {error}')
    if failures:
        raise RuntimeError(f'{original_error} Bereinigung unvollständig: '
                           + '; '.join(failures)) from original_error
