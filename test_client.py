from fastmcp import Client
import asyncio

async def main():
    # The client will automatically handle AWS Cognito OAuth
    async with Client("http://localhost:8000/mcp", auth="oauth") as client:
        # First-time connection will open AWS Cognito login in your browser
        print("✓ Authenticated with AWS Cognito!")

        # Test the protected tool
        print("Calling protected tool: get_access_token_claims")
        result = await client.call_tool("get_access_token_claims")
        user_data = result.data
        print("Available access token claims:")
        print(f"- sub: {user_data.get('sub', 'N/A')}")
        print(f"- username: {user_data.get('username', 'N/A')}")
        print(f"- cognito:groups: {user_data.get('cognito:groups', [])}")

if __name__ == "__main__":
    asyncio.run(main())