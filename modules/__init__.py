def get_modules(config):
    modules = []
    for module in config.options('Modules'):
        if config.getboolean('Modules', module):
            modules.append(getattr(__import__('modules.' + module), module))
    return modules