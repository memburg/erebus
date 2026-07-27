#!/usr/bin/env jruby

require "java"
require "optparse"
require "pathname"

java_import javax.imageio.ImageIO

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3
SUPPORTED_FORMATS = %w[png gif jpg jpeg bmp wbmp].freeze
MODE_ALIASES = {
  "cipher" => "cipher",
  "encrypt" => "cipher",
  "decipher" => "decipher",
  "decrypt" => "decipher"
}.freeze

def normalize_mode(mode)
  MODE_ALIASES.fetch(mode.strip.downcase.delete_prefix("=")) { raise ArgumentError, "Unsupported mode: #{mode}" }
end

def generate_sequence(rng, iterations, width, height, pivot = nil)
  Array.new(iterations) do
    direction = rng.rand(4)
    max_moves, pivot_size = direction <= DOWN ? [height, width] : [width, height]
    step_pivot = pivot ? pivot % pivot_size : rng.rand(pivot_size)
    [direction, rng.rand(1..max_moves), step_pivot]
  end
end

def apply_step(image, step)
  direction, moves, pivot = step
  horizontal = direction >= LEFT
  length = horizontal ? image.width : image.height
  fixed = pivot % (horizontal ? image.height : image.width)
  shift = moves % length
  shift = (length - shift) % length if direction == RIGHT || direction == DOWN
  return if shift.zero?

  pixels = Array.new(length) do |position|
    horizontal ? image.getRGB(position, fixed) : image.getRGB(fixed, position)
  end
  length.times do |position|
    color = pixels[(position + shift) % length]
    horizontal ? image.setRGB(position, fixed, color) : image.setRGB(fixed, position, color)
  end
end

def cipher(image, seed, iterations, pivot = nil)
  generate_sequence(Random.new(seed), iterations, image.width, image.height, pivot).each do |step|
    apply_step(image, step)
  end
end

def decipher(image, seed, iterations, pivot = nil)
  generate_sequence(Random.new(seed), iterations, image.width, image.height, pivot).reverse_each do |step|
    apply_step(image, [[DOWN, UP, RIGHT, LEFT][step[0]], step[1], step[2]])
  end
end

def output_path(path, mode)
  extension = path.extname.downcase.delete_prefix(".")
  extension = "png" unless SUPPORTED_FORMATS.include?(extension)
  name = "#{mode == "cipher" ? "c" : "d"}-#{path.basename(path.extname)}.#{extension}"
  [path.dirname.join(name), extension]
end

def process_image(path, mode, seed, iterations, show_size: false)
  image = ImageIO.read(java.io.File.new(path.to_s))
  raise "Failed to load image: #{path}" unless image

  puts "Image size: #{image.width}x#{image.height}" if show_size
  mode == "cipher" ? cipher(image, seed, iterations) : decipher(image, seed, iterations)
  destination, format = output_path(path, mode)
  raise "Failed to write output image: #{destination}" unless ImageIO.write(image, format, java.io.File.new(destination.to_s))

  destination
rescue java.lang.Exception => e
  raise "Failed to process '#{path}': #{e.message}"
end

def supported_images(path)
  path.children.select { |child| child.file? && SUPPORTED_FORMATS.include?(child.extname.downcase.delete_prefix(".")) }
      .sort_by { |child| child.basename.to_s.downcase }
end

def run(config)
  path = config[:path]
  if path.file?
    puts "Wrote output to: #{process_image(path, config[:mode], config[:seed], config[:iterations], show_size: true)}"
    return 0
  end
  unless path.directory?
    warn "Path does not exist: #{path}"
    return 1
  end

  images = supported_images(path)
  if images.empty?
    warn "No supported image files found in: #{path}"
    return 1
  end

  puts "Processing folder: #{path}"
  failures = []
  # ponytail: Plain counts preserve progress without keeping the ASCII-art module.
  print "\r0/#{images.length}"
  $stdout.flush
  images.each_with_index do |image, index|
    process_image(image, config[:mode], config[:seed], config[:iterations])
  rescue StandardError => e
    failures << [image, e.message]
  ensure
    print "\r#{index + 1}/#{images.length}"
    $stdout.flush
  end
  puts
  puts "Folder summary: #{images.length - failures.length} succeeded, #{failures.length} failed, #{images.length} total"
  unless failures.empty?
    puts "Failures:"
    failures.each { |image, error| puts "- #{image.basename}: #{error}" }
  end
  failures.empty? ? 0 : 1
end

def parse_args(argv)
  config = { mode: "cipher" }
  parser = OptionParser.new do |options|
    options.banner = "Usage: jruby src/erebus.rb IMAGE_OR_FOLDER SEED ITERATIONS [options]"
    options.on("-m MODE", "--mode=MODE", "Operation (default: cipher)") do |mode|
      config[:mode] = normalize_mode(mode)
    end
    options.on("-h", "--help", "Show this help") { puts options; exit }
  end
  parser.parse!(argv)
  raise OptionParser::MissingArgument, "IMAGE_OR_FOLDER SEED ITERATIONS" unless argv.length == 3

  config.merge(path: Pathname.new(argv[0]), seed: Integer(argv[1], 10), iterations: Integer(argv[2], 10)).tap do |parsed|
    raise OptionParser::InvalidArgument, "iterations must be a positive integer" if parsed[:iterations] < 1
  end
rescue OptionParser::ParseError, ArgumentError => e
  warn e.message
  warn parser
  exit 2
end

def prompt_config
  puts "Interactive mode"
  path = loop do
    print "Image or folder path: "
    raw = $stdin.readline.strip
    if raw.empty?
      puts "Please enter a file or folder path."
      next
    end
    candidate = Pathname.new(raw).expand_path
    break candidate if candidate.exist?
    puts "Path does not exist: #{candidate}"
  end
  mode = loop do
    print "Mode [encrypt/decrypt] (default: encrypt): "
    raw = $stdin.readline.strip
    break "cipher" if raw.empty?
    break normalize_mode(raw)
  rescue ArgumentError
    puts "Please choose encrypt or decrypt."
  end
  { path: path, mode: mode, iterations: prompt_integer("Iterations: ", 1), seed: prompt_integer("Seed: ") }
end

def prompt_integer(label, minimum = nil)
  loop do
    print label
    value = Integer($stdin.readline.strip, 10)
    if minimum && value < minimum
      puts "Value must be at least #{minimum}."
      next
    end
    return value
  rescue ArgumentError
    puts "Please enter a valid integer."
  end
end

if $PROGRAM_NAME == __FILE__
  begin
    exit run(ARGV.empty? ? prompt_config : parse_args(ARGV))
  rescue EOFError, Interrupt
    warn
    exit 1
  rescue StandardError => e
    warn e.message
    exit 1
  end
end
