family
======

Personal small website for my family

To create a superuser head into the shell and run the following commands:

> from apps.members.models import MemberUserManager
> MemberUserManager().create_superuser('<email>', '<password>', '<family_name>')
