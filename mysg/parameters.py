def write_parfile(filename, parameters):
    with open(filename, 'w') as f:
        for name in parameters:
            value = parameters[name]
            if isinstance(value, bytes):
                f.write("%s = %s\n" % (name, value.decode('ascii')))
            elif isinstance(value, str):
                f.write("%s = %s\n" % (name, value))
            else:
                f.write("%s = %9.3e\n" % (name, value))


def read_parfile(filename, nested=False):
    parameters = {}
    with open(filename) as f:
        for line in f:
            key, value = line.strip().split('=')
            try:
                key, value = key.strip(), float(value)
            except ValueError:
                key, value = key.strip(), value.strip()
            if nested:
                p = parameters
                components = key.split('.')
                for component in components[:-1]:
                    if component not in p:
                        p[component] = {}
                    p = p[component]
                p[components[-1]] = value
            else:
                parameters[key] = value
    return parameters
