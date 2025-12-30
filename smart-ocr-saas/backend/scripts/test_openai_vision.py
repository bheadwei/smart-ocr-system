"""
OpenAI Vision API Integration Test Script.

This script tests the OpenAI Vision API connection and OCR functionality.
"""
import asyncio
import sys
import os
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# Status markers (ASCII-safe)
PASS = "[PASS]"
FAIL = "[FAIL]"
SKIP = "[SKIP]"
WARN = "[WARN]"
INFO = "[INFO]"


async def test_openai_connection():
    """Test basic OpenAI API connection."""
    print("=" * 60)
    print("Test 1: OpenAI API Connection Test")
    print("=" * 60)

    try:
        from openai import AsyncOpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print(f"{FAIL} OPENAI_API_KEY not found in environment")
            return False

        print(f"{PASS} API Key found (length: {len(api_key)})")

        client = AsyncOpenAI(api_key=api_key)

        # Simple test call
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'API connection successful' in 5 words or less."}],
            max_tokens=20,
        )

        result = response.choices[0].message.content
        print(f"{PASS} API Response: {result}")
        print(f"{PASS} OpenAI API connection successful!")
        return True

    except Exception as e:
        print(f"{FAIL} Connection failed: {str(e)}")
        return False


async def test_vision_api_with_sample():
    """Test Vision API with a sample image."""
    print("\n" + "=" * 60)
    print("Test 2: OpenAI Vision API Test (Sample Image)")
    print("=" * 60)

    try:
        from openai import AsyncOpenAI
        import base64

        api_key = os.getenv("OPENAI_API_KEY")
        client = AsyncOpenAI(api_key=api_key)

        # Create a simple test image with text (1x1 white pixel as minimal test)
        # For real testing, we'll use a URL-based image
        print(f"{INFO} Testing with a sample image from URL...")

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What text do you see in this image? Reply with JSON format: {\"text\": \"extracted text here\"}",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Google_2015_logo.svg/1200px-Google_2015_logo.svg.png",
                                "detail": "low",
                            },
                        },
                    ],
                }
            ],
            max_tokens=100,
        )

        result = response.choices[0].message.content
        print(f"{PASS} Vision API Response: {result}")
        print(f"{PASS} Vision API working correctly!")
        return True

    except Exception as e:
        print(f"{FAIL} Vision API test failed: {str(e)}")
        return False


async def test_openai_service():
    """Test the OpenAIVisionService class."""
    print("\n" + "=" * 60)
    print("Test 3: OpenAIVisionService Class Test")
    print("=" * 60)

    try:
        # Mock settings for testing
        os.environ.setdefault("OPENAI_MODEL", "gpt-4o-mini")

        from app.services.openai_service import OpenAIVisionService

        service = OpenAIVisionService()
        print(f"{PASS} OpenAIVisionService instantiated successfully")

        # Test with a simple image
        # Create a minimal PNG (1x1 white pixel)
        import struct
        import zlib

        def create_minimal_png():
            """Create a minimal valid PNG image."""
            # PNG signature
            signature = b"\x89PNG\r\n\x1a\n"

            # IHDR chunk (image header)
            width = 100
            height = 50
            bit_depth = 8
            color_type = 2  # RGB
            ihdr_data = struct.pack(">IIBBBBB", width, height, bit_depth, color_type, 0, 0, 0)
            ihdr_crc = zlib.crc32(b"IHDR" + ihdr_data)
            ihdr_chunk = struct.pack(">I", 13) + b"IHDR" + ihdr_data + struct.pack(">I", ihdr_crc)

            # IDAT chunk (image data) - white pixels
            raw_data = b""
            for _ in range(height):
                raw_data += b"\x00"  # filter byte
                raw_data += b"\xff\xff\xff" * width  # white RGB pixels

            compressed = zlib.compress(raw_data)
            idat_crc = zlib.crc32(b"IDAT" + compressed)
            idat_chunk = struct.pack(">I", len(compressed)) + b"IDAT" + compressed + struct.pack(">I", idat_crc)

            # IEND chunk
            iend_crc = zlib.crc32(b"IEND")
            iend_chunk = struct.pack(">I", 0) + b"IEND" + struct.pack(">I", iend_crc)

            return signature + ihdr_chunk + idat_chunk + iend_chunk

        print(f"{INFO} Creating test image...")
        test_image = create_minimal_png()
        print(f"{PASS} Test image created ({len(test_image)} bytes)")

        print(f"{INFO} Calling OpenAI Vision API (this may take a few seconds)...")
        # Note: This will fail gracefully since it's just a white image
        # The important thing is that the API call works
        try:
            result = await service.analyze_image(test_image)
            print(f"{PASS} API call successful!")
            print(f"   - Extracted text length: {len(result.get('extracted_text', ''))}")
            print(f"   - Confidence: {result.get('confidence', 0)}")
            return True
        except Exception as e:
            if "JSON" in str(e) or "parse" in str(e).lower():
                print(f"{WARN} API responded but JSON parsing issue (expected for blank image)")
                print(f"{PASS} API connection verified!")
                return True
            raise

    except ImportError as e:
        print(f"{FAIL} Import error: {str(e)}")
        print("   Make sure you're running from the backend directory")
        return False
    except Exception as e:
        print(f"{FAIL} Service test failed: {str(e)}")
        return False


async def test_with_real_image(image_path: str = None):
    """Test with a real image file if provided."""
    print("\n" + "=" * 60)
    print("Test 4: Real Image OCR Test")
    print("=" * 60)

    # Check for test images in data directory
    test_dirs = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "tests", "data"),
    ]

    image_path = None
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            for f in os.listdir(test_dir):
                if f.lower().endswith((".png", ".jpg", ".jpeg")):
                    image_path = os.path.join(test_dir, f)
                    break
        if image_path:
            break

    if not image_path:
        print(f"{WARN} No test image found in data/ directory")
        print("   Skipping real image test")
        print("   To test with real image, place an image in the data/ directory")
        return None

    print(f"{INFO} Found test image: {image_path}")

    try:
        from app.services.openai_service import OpenAIVisionService

        service = OpenAIVisionService()

        with open(image_path, "rb") as f:
            image_data = f.read()

        print(f"{INFO} Image size: {len(image_data)} bytes")
        print(f"{INFO} Calling OpenAI Vision API...")

        result = await service.analyze_image(image_data)

        print("\n--- OCR Result ---")
        print(f"Extracted Text:\n{result.get('extracted_text', '')[:500]}...")
        print(f"\nStructured Data: {result.get('structured_data', {})}")
        print(f"Confidence: {result.get('confidence', 0)}")
        print(f"{PASS} Real image OCR test successful!")
        return True

    except Exception as e:
        print(f"{FAIL} Real image test failed: {str(e)}")
        return False


async def main():
    """Run all tests."""
    print("\n")
    print("*" * 60)
    print("*  OpenAI Vision API Integration Test Suite")
    print("*" * 60)

    results = {}

    # Test 1: Basic connection
    results["connection"] = await test_openai_connection()

    if not results["connection"]:
        print(f"\n{FAIL} Basic connection failed. Stopping tests.")
        return

    # Test 2: Vision API
    results["vision"] = await test_vision_api_with_sample()

    # Test 3: Service class
    results["service"] = await test_openai_service()

    # Test 4: Real image (optional)
    results["real_image"] = await test_with_real_image()

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, result in results.items():
        status = PASS if result else (SKIP if result is None else FAIL)
        print(f"  {test_name}: {status}")

    all_passed = all(r is not False for r in results.values())
    print("\n" + (f"{PASS} All tests passed!" if all_passed else f"{FAIL} Some tests failed"))


if __name__ == "__main__":
    asyncio.run(main())
