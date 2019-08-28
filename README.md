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

Please make sure not to use this command if it is not necessary (i.e. it is not picking up the current out of queue users), it is a heavy operation.