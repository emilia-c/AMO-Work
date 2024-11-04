require 'open-uri'
require 'fileutils'
require 'date'
require 'json'
require 'thread'

# Create a mutex for thread safety
semaphore = Mutex.new
@processed_file_count = 0
@all = false  # Adjust this variable based on your requirements

# Generate daily timestamps from 2021-01-01 to 2024-07-15
start_date = Date.new(2021, 1, 1)
end_date = Date.new(2024, 7, 15)
date_range = (start_date..end_date).to_a  # Create an array of dates

# Create an array of URLs with timestamps for each day
file_list_by_timestamp = date_range.map do |date|
  {
    url: 'https://www.europarl.europa.eu/meps/en/full-list/all',
    timestamp: date.strftime('%Y%m%d')  # Format date to YYYYMMDD
  }
end

# Function to check if a snapshot exists for a given date
def snapshot_exists?(url, timestamp)
  api_url = "https://archive.org/wayback/available?url=#{URI.encode(url)}&timestamp=#{timestamp}"
  response = URI.open(api_url).read
  data = JSON.parse(response)
  data['archived_snapshots'].any? { |_, snapshot| !snapshot['url'].nil? }
end

# Download logic
file_list_by_timestamp.each do |entry|
  file_url = entry[:url]
  file_timestamp = entry[:timestamp]
  file_path = "downloads/#{file_timestamp}_full_list.html"  # Adjust the path as needed

  # Check if snapshot exists for the date
  if snapshot_exists?(file_url, file_timestamp)
    unless File.exist?(file_path)
      begin
        # Create directory structure if it doesn't exist
        FileUtils.mkdir_p(File.dirname(file_path))
        open(file_path, "wb") do |file|
          begin
            # Fetch the snapshot from the Wayback Machine
            snapshot_url = "https://web.archive.org/web/#{file_timestamp}id_/#{file_url}"
            URI.open(snapshot_url, "Accept-Encoding" => "plain") do |uri|
              file.write(uri.read)
            end
          rescue OpenURI::HTTPError => e
            puts "(1) - #{file_url} # #{e}"
            if @all
              file.write(e.io.read)
              puts "(2) - #{file_path} saved anyway."
            end
          rescue StandardError => e
            puts "(3) - #{file_url} # #{e}"
            sleep(30)  # Wait before retrying
            retry
          end
        end
      rescue StandardError => e
        puts "(4) - #{file_url} # #{e}"
      ensure
        # Remove empty files if they exist
        if not @all && File.exist?(file_path) && File.size(file_path) == 0
          File.delete(file_path)
          puts "(5) - #{file_path} was empty and was removed."
        end
      end
      semaphore.synchronize do
        @processed_file_count += 1
        puts "(6) - #{file_url} -> #{file_path} (#{@processed_file_count}/#{file_list_by_timestamp.size})"
      end
      sleep(2)  # Pause between requests
    else
      semaphore.synchronize do
        @processed_file_count += 1
        puts "(7) - #{file_url} # #{file_path} already exists. (#{@processed_file_count}/#{file_list_by_timestamp.size})"
      end
    end
  else
    puts "No snapshot available for #{file_url} on #{file_timestamp}."
  end
end
