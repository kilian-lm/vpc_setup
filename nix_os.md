RaitoBezarius
Jun '23
There aren’t many other meaningful differences from a security perspective. If anything, since apparmor/selinux are
disabled by default, there are relatively fewer package maintainers, the package update cycle takes two weeks, and
things like secure boot are quite hard to achieve, NixOS is probably less secure.

I’d appreciate it if we did those comments with a clear threat model because they just push FUD on the Internet for no
reason. Not all security researchers agrees on the usefulness of AppArmor/SELinux vs. the new attack surface it
provides. :slight_smile:

Also, security is a sociotechnical problem, it is true that NixOS is more secure based on the simple fact that it’s not
a prime target for usage and development of payloads for this target is bound to not be a priority for attackers, except
if you are facing a customized attack towards you.

Containers and other pre-built binaries of various shapes cannot be tracked by nix with sufficient resolution to know
whether there are vulnerable blobs in them.

Huh? Containers built by Nix are perfectly trackable. What do you mean exactly by that?

Even when only using packages from nixpkgs, there are a small number of packages that simply download precompiled things
as well.

It is possible to filter out the source type to remove binary blobs, this metadata is not perfectly complete, but it
does exist in meta of many packages.

There’s no good way to automate checking for CVEs in such packages.

There was vulnix in the past, I don’t think it’s maintained anymore though it was transferred to nix-community.

And even if such packages were forbidden, there are plenty of applications which download further unvetted code at
runtime (usually proprietary, right now I’m using steam for example…).

nods But again, security research has to be discussed with a threat model in the context. If your threat model is to
defend against all type of runtime behaviors of your application, you probably need to distinguish server and desktop
usage.

In server usage, NixOS applies a fair amount of systemd hardening and continues to do so to all its services, not
everything is perfect, of course.

In desktop usage, this is a work in progress and to the best of my knowledge, https://spectrum-os.org/ 42 is working to
provide an interesting solution.

Don’t be lulled into a false sense of security just because you’re using NixOS. It’s always important to understand the
provenance of your software, even if nix really helps tracking most of it.

I’d rather say:

Define your threat model and what is acceptable to you or not as a risk
See if NixOS thwarts them because of incidental reasons or conscious decision choices
Provenance of the software is a tiny part of the problem, no matter what the supply chain security industry wants you to
believe. :slight_smile:
