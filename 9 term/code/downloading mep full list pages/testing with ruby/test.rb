require 'open-uri'
require 'json'
require 'uri'

url = 'https://www.europarl.europa.eu/meps/en/full-list/all'
timestamp = '20190521010718'  # Example timestamp

# Function to check if a snapshot exists
def snapshot_exists?(url, timestamp)
  # Use URI::DEFAULT_PARSER.escape to encode the URL
  encoded_url = URI::DEFAULT_PARSER.escape(url)
  api_url = "https://archive.org/wayback/available?url=#{encoded_url}&timestamp=#{timestamp}"
  
  response = URI.open(api_url).read
  data = JSON.parse(response)
  
  # Check if there is a valid snapshot
  !data['archived_snapshots'].empty? && !data['archived_snapshots']['closest'].nil?
end

# Check if snapshot exists for the provided URL and timestamp
if snapshot_exists?(url, timestamp)
  # Construct the snapshot URL
  snapshot_url = "https://web.archive.org/web/#{timestamp}/#{url}"
  
  begin
    response = URI.open(snapshot_url).read
    data = response  # Store or process the data as needed
    puts data
  rescue StandardError => e
    puts "Error fetching data: #{e.message}"
  end
else
  puts "No snapshot available for #{url} on #{timestamp}."
end
