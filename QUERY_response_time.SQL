# notes
#
# use issue 'number'
# 'number' is assigned chronologically & maps to PRs and IssueComments 
# as well as Issues
#
# ALSO: from github API: In the past, pull requests and issues were 
# more closely aligned than they are now. As far as the API is concerned, 
# every pull request is an issue, but not every issue is a pull request.
# This endpoint may also return pull requests in the response. 
# If an issue is a pull request, the object will include a pull_request key.
#
# INNER JOIN excludes issues that are still open AND
#            excludes issues that are were opened before begin date 
# take at least a year to capture this overlap
# order by number asc:
  > closed
  > closed		the before window
  > closed		(opened before date)
  -----------------
  > open
  > closed
  > open		the inclusive window
  > closed		INNER JOIN 
  > open
  > closed
  -----------------
  > open
  > open		the after (still open)
  > open
  -----------------
#
#
# note from the body of pull request number 21580 that was closed after only 30 seconds:
<!--
Pull requests without a rationale and clear improvement may be closed
 immediately.

Bitcoin Core has a thorough review process and even the most trivial change
needs to pass a lot of eyes and requires non-zero or even substantial time
effort to review. There is a huge lack of active reviewers on the project, so
patches often sit for a long time.
-->
# most <10 mins are spam
# investigate issues by web interface: https://github.com/bitcoin/bitcoin/issues/20940
# PRs can happen very fast as the author has already authored the commits; code review
# and merges can happen in hours (<day), see issue number 20216
#
# including all issues average days = 23.26
# excluding all issues <1 mins opened increased average days by 3.6% to 24.1
# excluding all issues <5 mins opened increased average days by 6.9% to 24.87
# excluding all issues <10 mins opened increased average days by 8.5% to 25.23
# excluding all issues <20 mins opened increased average days by 10.9% to 25.79
# excluding all issues <30 mins opened increased average days by 12.7% to 26.21
# excluding all issues <60 mins opened increased average days by 15.1% to 26.78
# excluding all issues <120 mins opened increased average days by 19.0% to 27.68
# not sure what to do with this
# 
#
# V I E W   I S S U E S  L I S T
#
WITH repo_name = 'bitcoin/bitcoin' AS repo
SELECT
    number, event_type,
	opened, 
	closed, 
	round(dateDiff('minute', toDateTime(opened), toDateTime(closed)), 2) AS mins_opened
FROM
(
    SELECT *
    FROM
   (
        SELECT 	number, event_type,
				created_at AS opened
		FROM github_events 
		WHERE 	repo AND
				(event_type = 'IssuesEvent' OR event_type = 'PullRequestEvent') AND
				action = 'opened' AND
				created_at >= toDateTime('2020-03-01')
    ) AS t1
    INNER JOIN
    (
        SELECT 	number, event_type,
				created_at AS closed
		FROM github_events 
		WHERE 	repo AND
				(event_type = 'IssuesEvent' OR event_type = 'PullRequestEvent') AND
				action = 'closed' AND
				created_at >= toDateTime('2020-03-01')
    ) AS t2 USING (number)
)
ORDER by mins_opened ASC
#
#
# V I E W   S I N G L E   I S S U E
#
SELECT *
FROM github_events 
WHERE repo_name = 'bitcoin/bitcoin' AND
      number = 19155
ORDER by created_at ASC
#
#
# A V E R A G E  C A L C U L A T I O N
#
WITH repo_name = 'bitcoin/bitcoin' AS repo,
     sum(dateDiff('minute', toDateTime(opened), toDateTime(closed)))/24/60 AS total_days,
     round(dateDiff('second', toDateTime(opened), toDateTime(closed)),2)/60 AS mins_open, 
	 count() AS num_issues,
     (event_type = 'IssuesEvent' OR event_type = 'PullRequestEvent') AS event,
     created_at >= toDateTime('2020-03-01') AS created
SELECT  round( total_days / num_issues, 2) AS average_days
FROM
(
    SELECT *
    FROM
   (
        SELECT 	number,
		created_at AS opened
	FROM github_events 
	WHERE 	repo AND
		event AND
		action = 'opened' AND
		created
    ) AS t1
    INNER JOIN
    (
        SELECT 	number,
		created_at AS closed
	FROM github_events 
	WHERE 	repo AND
		event AND
		action = 'closed' AND
		created
    ) AS t2 USING (number)
)
WHERE mins_open > 5



