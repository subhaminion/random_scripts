def _login_zendesk():
    '''
    Login to zendesk only once
    '''
    return zenpy.Zenpy(
        email=settings.ZENDESK_USER,
        token=settings.ZENDESK_TOKEN,
        subdomain=settings.ZENDESK_SUBDOMAIN
    )


def _create_zendesk_ticket(file, owner, z):
    """
    Creates Zendesk ticket, assigns to chief assignee, and adds file metadata
    """

    if file.zendesk_id or file.zendesk_id != 0:
        # The zendesk ticket exists. This is a rare scenario
        return file.zendesk_id

    try:
        # First, create a ticket
        ticket = z.tickets.create(
            zenpy.lib.api_objects.Ticket(
                subject='{} ({}/{}) [{}]'.format(
                    file.name, file.version, file.version_code, file.id),
                description='App has been uploaded',
                requester=zenpy.lib.api_objects.User(
                    name=owner.username,
                    email=owner.email,
                ),
                custom_fields=[
                    zenpy.lib.api_objects.CustomField(
                        id=41598289,
                        value=file.project.get_platform_display()),
                    zenpy.lib.api_objects.CustomField(
                        id=45173949,
                        value=file.id),
                ],
                priority='normal',
            )
        ).ticket

        # TODO use overhauled dbapi
        file.zendesk_id = ticket.id
        file.save()

        # Then, add a private comment with all file details
        ticket.comment = zenpy.lib.api_objects.Comment(
            body=(
                'User: {} ({})\n'
                'File: {} ({})\n'
                'Package: {}\n'
                'Version: {}\n'
                'Version code: {}\n'
                'MD5: {}\n'
                'SHA1: {}'.format(
                    owner.username, owner.id,
                    file.name, file.id,
                    file.project.package_name,
                    file.version,
                    file.version_code,
                    file.md5hash,
                    file.sha1hash
                )
            ),
            public=False,
        )
        ticket = z.tickets.update(ticket).ticket

        # Next, assign the ticket to the primary assignee
        ticket.assignee = z.users(id=settings.ZENDESK_DEFAULT_ASSIGNEE)
        z.tickets.update(ticket)
        return ticket.id

    except Exception as e:
        slack_error('Unexpected error while creating Zendesk ticket', str(e))
        return None


def _manual_scan_zendesk_update(file, z):
    try:
        ticket = z.tickets(id=file.zendesk_id)
        ticket.comment = zenpy.lib.api_objects.Comment(
            body='Manual application security assessment has been requested')
        ticket.tags = ['survey-request-pending']
        z.tickets.update(ticket)

    except zenpy.lib.exception.RecordNotFoundException as e:
        slack_error('Zendesk ticket {} for file {} not found'.format(
            file.zendesk_id, file.id), str(e))
    except Exception as e:
        slack_error(
            'Unexpected error while commenting on Zendesk ticket', str(e))


@token_required
def manual(request, file_id):
    '''
    API to request a manual assessment
    '''
    file = get_file(pk=file_id)
    _owner = file.project.owner
    if not can_read_file(user=request.user, file=file):
        return JsonResponse({
            'message': 'You dont have access to this file'
        })
    file.manual_requested()
    if settings.DEBUG or (_owner.is_staff or _owner.is_superuser):
        return JsonResponse({'message': 'Manual assessment not requested as '
                             'you are a staff user'})

    slack_alert(
        summary='*{}* ({}) requested {} manual assessment for *{}* ({})'.format(
            request.user.username, request.user.id,
            file.project.get_platform_display(), file.project.package_name,
            file.id),
        details=None,
        channel='#scans'
    )

    # Login to zenpy once only
    z = _login_zendesk()

    # Create or update ticket
    # FIXME: Needs to be more cleaner
    _create_zendesk_ticket(file, _owner, z)
    _manual_scan_zendesk_update(file, z)

    action.send(request.user, verb='requested manual scan', target=file)
    return JsonResponse({'message': 'Manual assessment requested'})
