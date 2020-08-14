# Copyright 2020 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import botocore.exceptions
from tempest.lib.common.utils import data_utils
from tempest.lib import decorators
import testtools

from ec2api_tempest_plugin import base
from ec2api_tempest_plugin import config

CONF = config.CONF


class S3Test(base.EC2TestCase):

    @decorators.idempotent_id('03e28c10-58b9-4729-a678-14e4166279be')
    @testtools.skipUnless(CONF.aws.s3_url, "s3_url is not defined")
    def test_create_delete_bucket(self):
        bucket_name = data_utils.rand_name('bucket')
        self.s3_client.create_bucket(Bucket=bucket_name)
        self.s3_client.head_bucket(Bucket=bucket_name)

        self.s3_client.delete_bucket(Bucket=bucket_name)
        try:
            self.s3_client.head_bucket(Bucket=bucket_name)
        except botocore.exceptions.ClientError as e:
            # If a client error is thrown, then check that it was a 404 error.
            # If it was a 404 error, then the bucket does not exist.
            error_code = e.response['Error']['Code']
            if error_code != '404':
                raise
