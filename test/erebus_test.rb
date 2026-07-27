require "minitest/autorun"
require_relative "../src/erebus"

java_import java.awt.image.BufferedImage

class ErebusTest < Minitest::Test
  def test_cipher_is_reversible
    image = BufferedImage.new(4, 3, BufferedImage::TYPE_INT_ARGB)
    original = Array.new(12) { |index| -0x1000000 | index }
    original.each_with_index { |color, index| image.setRGB(index % 4, index / 4, color) }

    cipher(image, 42, 100)
    decipher(image, 42, 100)

    assert_equal original, Array.new(12) { |index| image.getRGB(index % 4, index / 4) }
  end
end
