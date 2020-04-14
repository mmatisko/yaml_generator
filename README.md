# Yaml Generator

Tool for generating Ansible configuration from configuration template.  


## Requirements  

* [Python 3.6+](https://www.python.org/downloads/)
* Python libs - listed in requirements.txt
* Ansible - for using Ansible Vault feature (encrypted input/output configuration)

## Installation
No instalation required. Just need to clone this repository on target machine.

## Usage  
Could be used in your favourite command line/terminal application.

### Editor mode  

When you wanna edit you existing config (use with caution).  
Use with command line arguments, required mode argument is -E, possible combinations are listed below:  

Using static value
```sh
python3 yaml_gen.py -E -k KEY -v NEW_VALUE
```

Using network address
```sh
python3 yaml_gen.py -E -k KEY -n 192.168.11.0/24
```

Using port range
```sh
python3 yaml_gen.py -E -k KEY -p 4198-4205
```

Using file list (CSV file or "single item per line" text file)
```sh
python3 yaml_gen.py -E -k KEY -f ./ROCK_YOU.txt
```

### Generator mode  

Create new configurations from template using configuration file, see example file [generator_config.yml](https://github.com/mmatisko/yaml_generator/blob/master/include/generator_config.yml). Required mode argument is -G. 
File contains three sections:  
* General - generator config 
  * iteration count (required)
  * input folder (optional, would be overridden by cmd arg)
  * output folder (optional, would be overridden by cmd arg)
* Static - values for immediate write to config (could contain iterator variable), see using static value in Edit mode
* Dynamic - items used for generate writable values, see network address, port range and file list in Edit mode

#### Run
Generator mode example start command with parameters
* configuration file (required)
* output folder (optional, override outpuf_folder from configuration file from general section
```sh
python3 yaml_gen.py -G -c GENERATOR_CONF.yml -o .OUTPUT_FOLDER/
```

#### Iterator variable  
Used for variable part of static/dynamic values in generator mode. Simple notation is 
```http
<#>
```
which is altered in generator by index of iteration, started from 0 to (iterations_count - 1).  
Support basic math operators (+, -, *, /, %) with two operands, for instance addition:
```http
- network: 192.168.<#+1>.0/24
```

#### Ansible Vault feature
When using encrypted generator configuration file, Ansible configuration template or wanna encrypt generated configurations, has Yaml generator Ansible Vault feature support. This feature encrypts/decrypts files using AES256 algorithm. 

When starting generator you will be asked for template configuration password and for generator configuration file (if needed). If encrypted only part of template, only same part of generated configuration will be encrypted. Generated configurations describes table below.

| Template config | Provided password | Generated Configuration |
| ------ | ------ | ------ |
| Plain text | None | Plain text configuration|
| | New password | Encrypted using provided password |
| Encrypted using password | None | No configuration generated | 
| | Used password | Encrypted using provided password |

___
Caution: All encrypted file in template have to use same Ansible Vault password!  
___
Use with caution! When you lost/forget your Ansible Vault password, your configuration is lost!
