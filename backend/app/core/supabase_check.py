import asyncio

from supabase._async.client import AsyncClient


async def wait_for_supabase(supabase: AsyncClient):
    """Wait for Supabase to be ready for the operations we actually need"""
    max_retries = 30

    for attempt in range(max_retries):
        try:
            # Test the exact operations that will be used in seeding

            # 1. Test database table access (this was working)
            await supabase.table("tenants").select("count", count="exact").execute()
            print("Database table access verified", flush=True)

            # 2. Test auth admin list (this was working in health check)
            await supabase.auth.admin.list_users(page=1, per_page=1)
            print("Auth admin list_users working", flush=True)

            # 3. Test the EXACT failing operation - creating a user
            # Try creating a test user and immediately deleting it
            try:
                test_user = await supabase.auth.admin.create_user(
                    {
                        "email": f"test-{attempt}@example.com",
                        "password": "test123456",
                        "user_metadata": {"test": True},
                    }
                )

                # If it worked, clean up the test user
                if test_user.user:
                    await supabase.auth.admin.delete_user(test_user.user.id)
                    print(
                        "Auth admin create_user working - \
                        test user created and deleted",
                        flush=True,
                    )

                return  # All tests passed

            except Exception as create_error:
                print(f"create_user test failed: {create_error}", flush=True)
                if attempt == max_retries - 1:
                    raise create_error

        except Exception as e:
            if attempt == max_retries - 1:
                raise Exception(
                    f"Failed to connect after {max_retries} attempts: {e}"
                ) from e
            print(
                f"Waiting for Supabase create_user capability... \
                ({attempt + 1}/{max_retries}): {e}",
                flush=True,
            )
            await asyncio.sleep(3)  # Longer delay since we're testing more
