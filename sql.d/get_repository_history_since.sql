-- Copyright (C) 2016-2018 Dmitry Marakasov <amdmi3@amdmi3.ru>
--
-- This file is part of repology
--
-- repology is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
--
-- repology is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with repology.  If not, see <http://www.gnu.org/licenses/>.

--------------------------------------------------------------------------------
--
-- @param repo
-- @param since
--
-- @returns array of dicts
--
--------------------------------------------------------------------------------

-- intentionally broken, as repositories_history table is no longer updated
-- rust repology-webapp uses new repositories_history_new table
DO NOT SELECT
	ts AS timestamp,
	now() - ts AS timedelta,
	snapshot#>ARRAY[%(repo)s] AS snapshot
FROM repositories_history
WHERE ts >= now() - INTERVAL %(since)s
ORDER BY ts;
