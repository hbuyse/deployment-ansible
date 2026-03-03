--- Retrieve the latest version of clangd (absolute path)
---@return string filepath absolute path to the latest version of clangd
local function get_clangd_executable()
  local has_scan, scan = pcall(require, 'plenary.scandir')
  if not has_scan then
    return 'clangd'
  end

  local paths = os.getenv('PATH')
  if paths == nil then
    return 'clangd'
  end

  local list_clangd = { 'clangd', 'clangd-devel' }
  for i = 21, 18, -1 do
    table.insert(list_clangd, 'clangd' .. tostring(i))
    table.insert(list_clangd, 'clangd-' .. tostring(i))
  end

  -- gmatch returns an iterator function
  for path in paths:gmatch('([^:]+)') do
    local filepaths = scan.scan_dir(path, { hidden = false, search_pattern = 'clangd.*' })
    for _, clangd in ipairs(list_clangd) do
      for i = #filepaths, 1, -1 do
        local filepath = filepaths[i]
        if filepath == path .. '/' .. clangd then
          return filepath
        end
      end
    end
  end

  return 'clangd'
end

return {
  cmd = {
    get_clangd_executable(),
    '--background-index',
    '--clang-tidy',
    '--enable-config',
    '-j',
    '4',
  },
  root_markers = { '.clangd', 'compile_commands.json', '.git/' },
  filetypes = { 'c', 'cpp' },
}
