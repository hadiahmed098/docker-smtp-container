import re
import sys
import os
from enum import IntEnum, auto
from typing import TypedDict, Union

# ===== logger helpers
class LogType(IntEnum):
    INFO = auto()
    WARN = auto()
    ERROR = auto()

def _log(type:LogType, message:str):
    print(f"[tmpl_replace] [{type.name}] {message}", file=sys.stdout)

# ===== environment variable loaders
# << add env variable definition here
class EnvVariables(IntEnum):
    HOST_NAME = auto()          # A FQDN that identifies the host, should be what reverse DNS will point to
    DOMAIN_NAME = auto()        # Optional FQDN that resolves to this domain, defaults to $HOST_NAME
    ORIGIN_NAME = auto()        # Optional FQDN that mail will say its from, defaults to $DOMAIN_NAME

EnvVariableDict = dict[EnvVariables, str]

EnvVariableLoadOptions = Union[None,EnvVariables,str] # default value to load if not set (None signifies exit)

EnvVariableLoader = dict[EnvVariables, EnvVariableLoadOptions]

def _load_env_variables(env_load_dict: EnvVariableLoader) -> EnvVariableDict:
    output_dic:EnvVariableDict= {}
    for env_variable in env_load_dict.keys():
        try:
            output_dic[env_variable] = os.environ[env_variable.name]
        except KeyError:
            if env_load_dict[env_variable] == None:
                _log(LogType.ERROR, f"env variable {env_variable.name} must be defined")
                sys.exit(1)
            elif type(env_load_dict[env_variable]) is str:
                _log(LogType.WARN, f"env variable {env_variable.name} assuming default value")
                output_dic[env_variable] = env_load_dict[env_variable]
            else:
                _log(LogType.WARN, f"env variable {env_variable.name} assuming default value")
                output_dic[env_variable] = output_dic[env_load_dict[env_variable]]
    return output_dic

# ===== config file types
class ConfigOption(TypedDict):
    type: EnvVariables
    conditional: bool

ConfigOptionArray = list[ConfigOption]

ConfigFiles = dict[str, ConfigOptionArray]

def _make_ConfigOption(var:EnvVariables)->ConfigOption:
    return {"conditional": False, "type": var}

def _make_ConfigOptionConditional(var:EnvVariables)->ConfigOption:
    return {"conditional": True, "type": var}

# ===== process files
def _replace_key(str_buffer:str, key:EnvVariables, value:str, conditional:bool) -> str:
    if not conditional:
        return re.sub("{{\s*" + key.name + "\s*}}", value, str_buffer, 0, re.MULTILINE)
    else:
        pass

def _process_conf_files(env_vars:EnvVariableDict, file_list:ConfigFiles):
    for conf_file in file_list.keys():
        with open(f"{conf_file}.tmpl", "r") as conf_file_handle:
            conf_file_buffer = conf_file_handle.read()

            for conf_option in file_list[conf_file]:
                conf_file_buffer = _replace_key(conf_file_buffer, conf_option["type"], env_vars[conf_option["type"]], conf_option["conditional"])

            with open(conf_file, "w") as output_file_handle:
                output_file_handle.write(conf_file_buffer)

        _log(LogType.INFO, f"processed {conf_file}")


# << add env variable loading instructions here (add the definiton above!)
env_variables_to_load:EnvVariableLoader = {
    EnvVariables.HOST_NAME : None,
    EnvVariables.DOMAIN_NAME : EnvVariables.HOST_NAME,
    EnvVariables.ORIGIN_NAME : EnvVariables.DOMAIN_NAME
}

# << add any conf templates to process here
files_to_process:ConfigFiles = {
    "config/opendkim/opendkim.conf": [_make_ConfigOption(EnvVariables.DOMAIN_NAME)]
}

# ===== main entry point
def main():

    # First load all required env variables
    env_var_dict = _load_env_variables()

    # Now go through the config options
    _process_conf_files(env_var_dict)


# name guard
if __name__ == "__main__":
    main()
