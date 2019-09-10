import re

import models


def tag_handler(entry, form):
    """
    Processes and validates tag data from new entries and existing 
    entries being edited
    """

    old_tags = entry.tags.split()
    new_data = form.tags.data
    tag_pattern = re.compile(r"[#]\w+\b")
    new_tags = tag_pattern.findall(new_data)
    if old_tags:
        for tag in old_tags:
            if tag not in new_tags:
                try:
                    q = models.Tag.get(
                        models.Tag.topic == tag
                    )
                    entry_tag = models.EntryTag.get(
                        models.EntryTag.tag == q,
                        models.EntryTag.entry == entry,
                    )
                    entry_tag.delete_instance()
                except:
                    pass
    for tag in new_tags:
        try:
            new_tag = models.Tag.get(
                models.Tag.topic == tag
            )
        except models.DoesNotExist:
            new_tag = models.Tag.create(
                topic=tag
            )
        try:
            models.EntryTag.create(
                entry=entry,
                tag=new_tag,
            )
        except models.IntegrityError:
            pass


def delete_tag_handler(entry):
    """
    Deletes existing tags if blank tag field is submitted on edit view
    """

    delete_all_tags_query = models.EntryTag.select().where(
        models.EntryTag.entry == entry,
    )
    for instance in delete_all_tags_query:
        instance.delete_instance()


def resource_handler(entry, form):
    """
    Processes and validates resource data from new entries and existing 
    entries being edited
    """

    new_resources = form.resources.data.strip().splitlines()
    old_resources = entry.resources.splitlines()
    url_pattern = re.compile(
        r"(\b(http[s]*:\/\/|(www\.))(\S)*\b/?)")

    for resource in old_resources:
        if resource not in new_resources:
            url_match = url_pattern.search(resource)
            title = re.sub(url_pattern, "", resource)
            cleaned_title = cleaned_title = re.sub(
                r"[\b|\b]", "", title)
            try:
                query = models.Resource.get(
                    models.Resource.title == cleaned_title,
                    models.Resource.entry == entry,
                )
                query.delete_instance()
            except:
                pass

    for line in new_resources:
        url_match = url_pattern.search(line)
        title = re.sub(url_pattern, "", line)
        cleaned_title = cleaned_title = re.sub(
            r"[\b|\b]", "", title)
        if url_match == None:
            try:
                models.Resource.get(
                    models.Resource.title == cleaned_title,
                    models.Resource.link == None,
                )
            except models.DoesNotExist:
                models.Resource.create(
                    entry=entry,
                    title=cleaned_title,
                    link=None,
                )
        else:
            try:
                models.Resource.get(
                    models.Resource.title == cleaned_title,
                    models.Resource.link == url_match[0],
                )
            except models.DoesNotExist:
                models.Resource.create(
                    entry=entry,
                    title=cleaned_title,
                    link=url_match[0],
                )


def delete_resource_handler(entry):
    """
    Deletes existing resources if blank resource field is submitted on edit view
    """

    delete_all_resources_query = models.Resource.select().where(
        models.Resource.entry == entry,
    )
    for instance in delete_all_resources_query:
        instance.delete_instance()
