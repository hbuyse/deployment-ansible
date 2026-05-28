return {
  cmd = { 'neocmakelsp', 'stdio' },
  filetypes = { 'cmake' },
  root_markers = {
    'CMakePresets.json',
    'CTestConfig.cmake',
    '.git/',
    'build/',
    'cmake/',
  },
  single_file_support = true,
  init_options = {
    format = {
      enable = true,
    },
    lint = {
      enable = true,
    },
    scan_cmake_in_package = true, -- default is true
  },
}
