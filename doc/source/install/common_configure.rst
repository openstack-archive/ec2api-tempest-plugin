2. Edit the ``/etc/ec2api_tempest_plugin/ec2api_tempest_plugin.conf`` file and complete the following
   actions:

   * In the ``[database]`` section, configure database access:

     .. code-block:: ini

        [database]
        ...
        connection = mysql+pymysql://ec2api_tempest_plugin:EC2API_TEMPEST_PLUGIN_DBPASS@controller/ec2api_tempest_plugin
