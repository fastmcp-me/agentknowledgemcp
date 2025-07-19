#!/usr/bin/env python3
"""
Demo: So sánh cách sử dụng tools file trước và sau khi hợp nhất
"""

def demo_old_way():
    """Minh họa cách sử dụng tools file trước đây (10 tools riêng lẻ)"""
    print("🔴 CÁCH CŨ - 10 Tools Riêng Lẻ:")
    print("=" * 50)
    
    # Trước đây phải nhớ và sử dụng 10 tools khác nhau
    print("1. Đọc file:")
    print("   read_file(file_path='/path/file.txt', encoding='utf-8')")
    print()
    
    print("2. Ghi file:")
    print("   write_file(file_path='/path/file.txt', content='data', encoding='utf-8', create_dirs=True)")
    print()
    
    print("3. Thêm nội dung:")
    print("   append_file(file_path='/path/file.txt', content='more data', encoding='utf-8')")
    print()
    
    print("4. Xóa file:")
    print("   delete_file(file_path='/path/file.txt')")
    print()
    
    print("5. Di chuyển file:")
    print("   move_file(source_path='/path/old.txt', destination_path='/path/new.txt', create_dirs=True)")
    print()
    
    print("6. Sao chép file:")
    print("   copy_file(source_path='/path/file.txt', destination_path='/path/copy.txt', create_dirs=True)")
    print()
    
    print("7. Thông tin file:")
    print("   file_info(path='/path/file.txt')")
    print()
    
    print("8. Liệt kê thư mục:")
    print("   list_directory(directory_path='/path', include_hidden=False, recursive=False)")
    print()
    
    print("9. Tạo thư mục:")
    print("   create_directory(directory_path='/path/newdir', parents=True)")
    print()
    
    print("10. Xóa thư mục:")
    print("    delete_directory(directory_path='/path/dir', recursive=False)")
    print()
    
    print("❌ Nhược điểm:")
    print("   • Phải nhớ 10 tên tools khác nhau")
    print("   • Tên parameters không nhất quán (file_path vs directory_path vs path)")
    print("   • Khó sử dụng cho người mới")
    print("   • Code phức tạp khi cần nhiều thao tác")
    print()

def demo_new_way():
    """Minh họa cách sử dụng tool unified edit_file"""
    print("🟢 CÁCH MỚI - 1 Tool Thống Nhất:")
    print("=" * 50)
    
    # Giờ chỉ cần nhớ 1 tool với parameter operation
    print("1. Đọc file:")
    print("   edit_file(operation='read', path='/path/file.txt', encoding='utf-8')")
    print()
    
    print("2. Ghi file:")
    print("   edit_file(operation='write', path='/path/file.txt', content='data', encoding='utf-8', create_dirs=True)")
    print()
    
    print("3. Thêm nội dung:")
    print("   edit_file(operation='append', path='/path/file.txt', content='more data', encoding='utf-8')")
    print()
    
    print("4. Xóa file:")
    print("   edit_file(operation='delete', path='/path/file.txt')")
    print()
    
    print("5. Di chuyển file:")
    print("   edit_file(operation='move', path='/path/old.txt', destination='/path/new.txt', create_dirs=True)")
    print()
    
    print("6. Sao chép file:")
    print("   edit_file(operation='copy', path='/path/file.txt', destination='/path/copy.txt', create_dirs=True)")
    print()
    
    print("7. Thông tin file:")
    print("   edit_file(operation='info', path='/path/file.txt')")
    print()
    
    print("8. Liệt kê thư mục:")
    print("   edit_file(operation='list', path='/path', include_hidden=False, recursive=False)")
    print()
    
    print("9. Tạo thư mục:")
    print("   edit_file(operation='mkdir', path='/path/newdir', create_dirs=True)")
    print()
    
    print("10. Xóa thư mục:")
    print("    edit_file(operation='rmdir', path='/path/dir', recursive=False)")
    print()
    
    print("✅ Ưu điểm:")
    print("   • Chỉ cần nhớ 1 tool duy nhất: edit_file")
    print("   • Parameter names nhất quán (luôn là 'path')")
    print("   • Dễ học và sử dụng")
    print("   • Code gọn gàng và rõ ràng")
    print("   • IntelliSense tốt hơn trong IDE")
    print()

def demo_workflow_comparison():
    """So sánh workflow thực tế"""
    print("🔄 SO SÁNH WORKFLOW THỰC TẾ:")
    print("=" * 50)
    
    print("📋 Task: Tạo file config, backup, và cleanup")
    print()
    
    print("🔴 Cách cũ (10 tool calls):")
    print("""
    # 1. Tạo thư mục
    create_directory(directory_path='/app/config', parents=True)
    
    # 2. Tạo file config
    write_file(
        file_path='/app/config/settings.json', 
        content='{"debug": true}',
        create_dirs=True
    )
    
    # 3. Backup file
    copy_file(
        source_path='/app/config/settings.json',
        destination_path='/app/config/settings.backup.json',
        create_dirs=True
    )
    
    # 4. Kiểm tra file info
    file_info(path='/app/config/settings.json')
    
    # 5. Liệt kê để verify
    list_directory(directory_path='/app/config', include_hidden=False)
    
    # 6. Cleanup: xóa backup
    delete_file(file_path='/app/config/settings.backup.json')
    """)
    
    print("🟢 Cách mới (6 tool calls với cùng 1 tool):")
    print("""
    # 1. Tạo thư mục  
    edit_file(operation='mkdir', path='/app/config', create_dirs=True)
    
    # 2. Tạo file config
    edit_file(
        operation='write', 
        path='/app/config/settings.json',
        content='{"debug": true}',
        create_dirs=True
    )
    
    # 3. Backup file
    edit_file(
        operation='copy',
        path='/app/config/settings.json', 
        destination='/app/config/settings.backup.json',
        create_dirs=True
    )
    
    # 4. Kiểm tra file info
    edit_file(operation='info', path='/app/config/settings.json')
    
    # 5. Liệt kê để verify
    edit_file(operation='list', path='/app/config', include_hidden=False)
    
    # 6. Cleanup: xóa backup
    edit_file(operation='delete', path='/app/config/settings.backup.json')
    """)
    
    print("💡 Nhận xét:")
    print("   • Cùng số lượng thao tác nhưng interface nhất quán")
    print("   • Dễ đọc và hiểu code hơn")
    print("   • IntelliSense chỉ cần gợi ý 1 tool")
    print("   • Error messages thống nhất")
    print()

def demo_parameter_consistency():
    """So sánh tính nhất quán của parameters"""
    print("🎯 TÍNH NHẤT QUÁN CỦA PARAMETERS:")
    print("=" * 50)
    
    print("🔴 Cách cũ - Parameters không nhất quán:")
    print("""
    read_file(file_path='/path')           # file_path
    write_file(file_path='/path')          # file_path  
    list_directory(directory_path='/path') # directory_path
    file_info(path='/path')                # path
    create_directory(directory_path='/path', parents=True)  # directory_path + parents
    move_file(source_path='/a', destination_path='/b')      # source_path + destination_path
    """)
    
    print("🟢 Cách mới - Parameters hoàn toàn nhất quán:")
    print("""
    edit_file(operation='read', path='/path')
    edit_file(operation='write', path='/path')
    edit_file(operation='list', path='/path')  
    edit_file(operation='info', path='/path')
    edit_file(operation='mkdir', path='/path', create_dirs=True)
    edit_file(operation='move', path='/a', destination='/b')
    """)
    
    print("✅ Lợi ích:")
    print("   • Luôn luôn là 'path' cho đường dẫn chính")
    print("   • 'destination' cho đường dẫn đích (nếu có)")
    print("   • Các optional parameters có tên nhất quán")
    print("   • Không cần nhớ file_path vs directory_path vs path")
    print()

if __name__ == "__main__":
    print("🎪 DEMO: File Tools Unification")
    print("=" * 60)
    print()
    
    demo_old_way()
    print()
    
    demo_new_way() 
    print()
    
    demo_workflow_comparison()
    print()
    
    demo_parameter_consistency()
    
    print("🎉 Kết luận:")
    print("   Tool edit_file thống nhất đã đơn giản hóa đáng kể")
    print("   việc làm việc với files từ 10 tools → 1 tool duy nhất!")
    print("   Dễ sử dụng hơn, nhất quán hơn, và maintainable hơn.")
    print()
