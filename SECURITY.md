# Security Policy

## Supported Versions

Security fixes are made on the latest minor release only. Upgrade to the newest
release before reporting.

| Version | Supported |
| ------- | --------- |
| 2.0.x   | Yes       |
| < 2.0   | No        |

## Reporting a Vulnerability

Report vulnerabilities privately through GitHub's
[private vulnerability reporting](https://github.com/arunderwood/pychrony/security/advisories/new)
(the **Report a vulnerability** button on the repository's Security tab). Do not
open a public issue.

Include the pychrony version, how it was installed (wheel or source build), the
libchrony and chrony versions, and steps to reproduce.

## Scope

pychrony is a read-only monitoring library: it reads chronyd's `tracking`,
`sources`, `sourcestats` and `rtcdata` reports and never controls chronyd.

How chronyd is exposed is the deployment's concern, not pychrony's. In
particular, chronyd's command port is unauthenticated, and the Unix socket is a
full control channel. See
[Choosing a Transport](https://pychrony.org/#choosing-a-transport) and
[Remote and Custom Connections](https://pychrony.org/#remote-and-custom-connections)
for what each transport exposes and how to configure it. Vulnerabilities in
chrony or libchrony themselves belong with the
[chrony project](https://chrony-project.org/), though a flaw in the libchrony
copy bundled in pychrony's wheels is in scope here.
