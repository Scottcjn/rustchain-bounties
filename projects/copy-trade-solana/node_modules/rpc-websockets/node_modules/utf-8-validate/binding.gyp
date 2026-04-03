{
  'variables': {
    'openssl_fips': ''
  },
  'targets': [
    {
      'target_name': 'validation',
      'sources': [
        'src/validation.cc',
        'deps/is_utf8/src/is_utf8.cpp'
      ],
      'cflags_cc': ['-std=gnu++11'],
      'conditions': [
        ["OS=='mac'", {
          'xcode_settings': {
            'MACOSX_DEPLOYMENT_TARGET': '10.7'
          }
        }]
      ]
    }
  ]
}
