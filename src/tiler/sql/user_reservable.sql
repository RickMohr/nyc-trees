(SELECT
  block.geom,
  block.id,
  turf.group_id,
  core_group.slug AS group_slug,
  CASE
    WHEN (block.is_available AND reservation.id IS NULL
          AND (turf.id IS NULL
               OR trustedmapper.id IS NOT NULL
               OR core_group.admin_id = <%= user_id %>)) THEN 'available'
    -- If a blockface is currently reserved, we should make it look
    -- 'available'.  We use a GeoJSON layer in the UI for the user's
    -- reserved blockfaces, and when a blockface is deselected we want to
    -- be able to reselect it
    WHEN reservation.user_id IS NOT DISTINCT FROM <%= user_id %> THEN 'available'
    ELSE 'unavailable'
  END AS survey_type,
  CASE
    WHEN reservation.id IS NOT NULL AND reservation.user_id <> <%= user_id %> THEN 'reserved'
    WHEN (core_group.id IS NOT NULL
          AND NOT core_group.allows_individual_mappers) THEN 'unavailable'
    WHEN NOT block.is_available THEN 'unavailable'
    -- We should only allow requesting access to active groups that you are
    -- not already a trusted mapper or admin of
    WHEN (turf.id IS NOT NULL
          AND (core_group.is_active = TRUE
               AND trustedmapper.id IS NULL
               AND core_group.admin_id <> <%= user_id %>)) THEN 'group_territory'
    -- If a group is inactive, it is unavailable unless you are an admin or
    -- a trusted mapper of that group
    WHEN (turf.id IS NOT NULL
          AND core_group.is_active = FALSE
          AND trustedmapper.id IS NULL
          AND core_group.admin_id <> <%= user_id %>) THEN 'unavailable'
    ELSE 'none'
  END AS restriction
  FROM survey_blockface AS block
  LEFT OUTER JOIN survey_territory AS turf
    ON block.id = turf.blockface_id
  LEFT JOIN core_group ON core_group.id = turf.group_id
  LEFT OUTER JOIN survey_blockfacereservation AS reservation
    ON (block.id = reservation.blockface_id
        AND reservation.canceled_at IS NULL
        AND reservation.expires_at > now() at time zone 'utc')
  LEFT OUTER JOIN users_trustedmapper AS trustedmapper
    ON (turf.group_id = trustedmapper.group_id
        AND trustedmapper.user_id = <%= user_id %>
        AND trustedmapper.is_approved)
) AS query
