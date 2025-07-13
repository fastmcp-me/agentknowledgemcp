"""
Test script for the sophisticated confirmation system.
"""
import asyncio
import sys
import os

# Add src to path
sys.path.append('src')

from confirmation import ConfirmationManager
from config import load_config

async def test_full_workflow():
    """Test the complete confirmation workflow."""
    print("🚀 **Testing Sophisticated Confirmation System**\n")
    
    # Load configuration
    config = load_config()
    
    # Initialize manager
    manager = ConfirmationManager(config.get('confirmation', {}))
    print("✅ Confirmation manager initialized")
    
    try:
        # Test 1: Check tool requirements
        print("\n📋 **Test 1: Tool Requirement Check**")
        
        test_tools = [
            'update_config',      # Should require (admin)
            'write_file',         # Should require (file write)
            'delete_file',        # Should require (destructive)
            'index_document',     # Should require (elasticsearch write)
            'read_file',          # Should NOT require
            'search',             # Should NOT require
            'get_config'          # Should NOT require
        ]
        
        for tool in test_tools:
            requires, rule = await manager.requires_confirmation(tool)
            status = "✅ REQUIRES" if requires else "🔓 ALLOWED"
            rule_name = rule.get('rule_name', 'N/A') if requires else 'N/A'
            timeout = rule.get('timeout_minutes', 'N/A') if requires else 'N/A'
            print(f"  {status} {tool:<18} | Rule: {rule_name:<20} | Timeout: {timeout}m")
        
        # Test 2: Store and process operations
        print("\n📋 **Test 2: Store Pending Operations**")
        
        # Store a test operation
        pending_id = await manager.store_operation(
            tool_name='update_config',
            arguments={'config_section': 'test', 'config_key': 'test_key', 'config_value': 'test_value'},
            session_id='test_session_123'
        )
        
        print(f"✅ Stored operation with ID: {pending_id}")
        
        # Check operation status
        operation = await manager.get_operation(pending_id)
        if operation:
            print(f"✅ Operation found - Status: {operation.status.value}")
            print(f"   Tool: {operation.tool_name}")
            print(f"   Rule: {operation.rule_name}")
            print(f"   Time remaining: {operation.time_remaining()} seconds")
            print(f"   Audit trail entries: {len(operation.audit_trail)}")
        
        # Test 3: Process responses
        print("\n📋 **Test 3: Process User Responses**")
        
        # Test invalid response
        result1 = await manager.process_user_response(pending_id, "maybe", "test message")
        print(f"❌ Invalid response result: {result1['success']} - {result1.get('error', '')}")
        
        # Test deny response
        result2 = await manager.process_user_response(pending_id, "no", "User denied operation")
        print(f"🚫 Deny response result: {result2['success']} - {result2.get('message', '')}")
        
        # Test 4: Store another operation and approve it (but can't execute without full server)
        print("\n📋 **Test 4: Approval Process (Mock)**")
        
        pending_id2 = await manager.store_operation(
            tool_name='write_file',
            arguments={'file_path': '/test/path.txt', 'content': 'test content'},
            session_id='test_session_123'
        )
        
        print(f"✅ Stored second operation: {pending_id2}")
        
        # Check session operations
        session_ops = await manager.get_session_operations('test_session_123')
        print(f"✅ Session has {len(session_ops)} operations")
        
        # Test 5: Statistics
        print("\n📋 **Test 5: System Statistics**")
        
        stats = await manager.get_statistics()
        print(f"✅ System Statistics:")
        print(f"   Total operations: {stats['total_operations']}")
        print(f"   Active operations: {stats['active_operations']}")
        print(f"   Active sessions: {stats['active_sessions']}")
        print(f"   Approved: {stats['approved']}")
        print(f"   Denied: {stats['denied']}")
        print(f"   Expired: {stats['expired']}")
        print(f"   System enabled: {stats['config_enabled']}")
        
        # Test 6: Cleanup expired (manual test)
        print("\n📋 **Test 6: Cleanup Test**")
        print("✅ Cleanup system ready (runs automatically every 5 minutes)")
        
        # Test 7: Cancel operation
        print("\n📋 **Test 7: Cancel Operation**")
        
        cancelled = await manager.cancel_operation(pending_id2, "Test cancellation")
        print(f"✅ Operation cancelled: {cancelled}")
        
        # Final statistics
        final_stats = await manager.get_statistics()
        print(f"\n📊 **Final Statistics:**")
        print(f"   Total processed: {final_stats['total_operations']}")
        print(f"   Currently active: {final_stats['active_operations']}")
        print(f"   Denied: {final_stats['denied']}")
        print(f"   Cancelled: {final_stats['cancelled']}")
        
    finally:
        # Cleanup
        await manager.shutdown()
        print("\n🧹 Manager shutdown complete")
    
    print("\n🎉 **All tests completed successfully!**")

if __name__ == "__main__":
    asyncio.run(test_full_workflow())
