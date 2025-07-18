def set_active_link(app_name:str = "default") -> dict[str, str]:
    return {f'{app_name}_active_link': "bg-lime-300" if app_name != "default" else "bg-gray-300"}


def set_headtitle_and_active_link(title_name:str, link_name:str, *args) -> dict[str, str]:
    site_title = f"{title_name} SMA IT AL BINAA"
    if args:
        additional_title = " ".join(args)
        site_title = " ".join([site_title, additional_title])
    context = {"site_title": site_title}
    context.update(set_active_link(link_name))
    return context