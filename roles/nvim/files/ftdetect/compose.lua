-- Detect yaml.docker-compoe filetype
if vim.filetype then
  vim.filetype.add({
    filename = {
      ['docker-compose.yml'] = 'yaml.docker-compose',
      ['docker-compose.yaml'] = 'yaml.docker-compose',
      ['compose.yml'] = 'yaml.docker-compose',
      ['compose.yaml'] = 'yaml.docker-compose',
    },
  })
else
  vim.api.nvim_create_autocmd({ 'BufRead', 'BufNewFile' }, {
    pattern = {
      'docker-compose.yml',
      'docker-compose.yaml',
      'compose.yml',
      'compose.yaml',
    },
    callback = function()
      vim.bo.filetype = 'yaml.docker-compose'
    end,
  })
end
