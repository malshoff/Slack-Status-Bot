# Slack-Status-Bot
Slack bot that modifies user statuses according to their current availability (pulled from the Roster)

## Supported Commands:
Authorize the Out of Queue Bot and/or have it update your status on your OOQ day manually:

```
/ooq run
```

List Out of Queue engineers in the #sup-ooq channel:

```
/ooq list
```

List Out of Queue engineers in the #sup-pcf-staff (only specific users may use this):

```
/ooq listall
```

Update the status of all OOQ engineers (only specific users may use this):

```
/ooq runall
```

Refresh the slack bot:

```
/ooq refresh
```

Update the out of queue db with current CEs. This is performed automatically every morning at 8:30 EST, but can be executed by command as well. Please make sure to use this command only when necessary (i.e. it is not picking up the current out of queue users, or you updated your status after 8:30 EST)
