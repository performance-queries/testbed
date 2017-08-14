Steps to run the Marple demo:

1. Run `./run_demo.sh $json`, where $json is the compiled query you want to run. You will have to type in the superuser password.

Note: To set this up on a different machine, some extra steps are needed:
- sswitch_CLI sets the $PYTHONPATH, but sudo does not keep environment variables of the user (at least on Amazon AWS instances).
So if you try to invoke the behavioral model CLI from sudo python, you will likely get the following error:

`ImportError: No module named thrift`

because the thrift module, used by the CLI, is not in the env list for sudo.
To fix this, you have to edit the /etc/sudoers file (by using the `sudo visudo` command) and add the following line:

`DEFAULTS   env_keep += "PYTHONPATH"`

after the `DEFAULTS env_reset` line. The error should go away.

