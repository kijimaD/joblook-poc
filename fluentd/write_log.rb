require 'json'

while line = STDIN.gets
  record = JSON.parse(line)
  file_path = record['file_path']

  File.open(file_path, 'a') do |f|
    f.puts(record.to_json)
  end
end

# テスト
# echo '{"task_id":"12345","message":"Test log","file_path":"/fluentd/etc/log/aaa.log"}' | ruby /fluentd/etc/write_log.rb
