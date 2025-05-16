#!/usr/bin/env python3
#coding:utf-8
import lldb
import optparse
import shlex
import re

# 获取ASLR偏移地址
def get_ASLR(library_name=None):
    """
    获取指定库或主程序的ASLR偏移地址
    
    参数:
        library_name: 动态库名称，如果为None则获取主程序的偏移
    
    返回:
        成功返回偏移地址字符串(0x格式)，失败返回None
    """
    interpreter = lldb.debugger.GetCommandInterpreter()
    returnObject = lldb.SBCommandReturnObject()
    
    if library_name:
        # 使用精确命令直接查找指定库
        interpreter.HandleCommand(f'image list -o -f {library_name}', returnObject)
    else:
        # 获取所有加载的镜像，第一个通常是主程序
        interpreter.HandleCommand('image list -o', returnObject)
    
    output = returnObject.GetOutput()
    
    # 如果有输出，尝试匹配第一个偏移地址
    if output.strip():
        if not library_name:
            # 对于主程序，只取第一行
            first_line = output.split('\n')[0]
            match = re.search(r'0x[0-9a-fA-F]+', first_line)
            if match:
                return match.group(0)
        else:
            # 对于库，匹配任意行中的地址
            match = re.search(r'0x[0-9a-fA-F]+', output)
            if match:
                return match.group(0)
    
    return None

# Super breakpoint - 增强版断点设置
def sbr(debugger, command, result, internal_dict):
    """
    设置带ASLR偏移的断点
    
    用法: sbr <address> [library_name]
    
    示例:
      sbr 0x1000                 # 在主程序偏移0x1000处设置断点
      sbr 0x1000 libsystem_c.dylib  # 在指定库偏移0x1000处设置断点
    """
    args = shlex.split(command)
    
    if len(args) == 0:
        print('Usage: sbr <address> [library_name]', file=result)
        return
    
    address = args[0]
    library_name = None if len(args) < 2 else args[1]
    
    ASLR = get_ASLR(library_name)
    if ASLR:
        if library_name:
            print(f"Setting breakpoint at {library_name} offset {address}", file=result)
        debugger.HandleCommand(f'br set -a "{ASLR}+{address}"')
    else:
        if library_name:
            print(f"Library '{library_name}' not found or ASLR not available!", file=result)
        else:
            print('ASLR not found!', file=result)

# Get Address - 增强版地址计算
def adr(debugger, command, result, internal_dict):
    """
    计算地址偏移或偏移地址
    
    用法:
      adr <memory_address> [library_name]  # 计算内存地址相对于库的偏移
      adr +<offset> [library_name]         # 计算偏移对应的实际内存地址
    
    示例:
      adr 0x100003f80             # 计算内存地址相对于主程序的偏移
      adr 0x100003f80 libsystem   # 计算内存地址相对于libsystem的偏移
      adr +0x3f80                 # 计算主程序偏移0x3f80对应的内存地址
      adr +0x3f80 libsystem       # 计算libsystem偏移0x3f80对应的内存地址
    """
    args = shlex.split(command)
    
    if len(args) == 0:
        print('Usage: adr <memory_address/+offset> [library_name]', file=result)
        return
    
    address_or_offset = args[0]
    library_name = None if len(args) < 2 else args[1]
    
    ASLR = get_ASLR(library_name)
    if not ASLR:
        if library_name:
            print(f"Library '{library_name}' not found or ASLR not available!", file=result)
            # 尝试列出可能的库，帮助用户找到正确的库名
            debugger.HandleCommand(f'image list | grep -i {library_name}')
        else:
            print('ASLR not found!', file=result)
        return
    
    ASLR_int = int(ASLR, 16)
    
    # 检查是计算偏移还是计算地址
    if address_or_offset.startswith('+'):
        # 计算偏移对应的内存地址
        try:
            offset_value = int(address_or_offset[1:], 16) if address_or_offset[1:].startswith('0x') else int(address_or_offset[1:], 0)
            memory_address = ASLR_int + offset_value
            lib_info = f" in {library_name}" if library_name else ""
            print(f"Address: {format(memory_address, '#x')} | Offset: {format(offset_value, '#x')}{lib_info} | ASLR: {ASLR}", file=result)
        except ValueError:
            print(f"Invalid offset format: {address_or_offset}", file=result)
    else:
        # 计算内存地址的偏移
        try:
            memory_address_int = int(address_or_offset, 16) if address_or_offset.startswith('0x') else int(address_or_offset, 0)
            offset_value = memory_address_int - ASLR_int
            lib_info = f" from {library_name}" if library_name else ""
            print(f"Offset: {format(offset_value, '#x')}{lib_info} | Address: {format(memory_address_int, '#x')} | ASLR: {ASLR}", file=result)
        except ValueError:
            print(f"Invalid address format: {address_or_offset}", file=result)

# 初始化模块，添加命令
def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f %s.sbr sbr' % __name__)
    debugger.HandleCommand('command script add -f %s.adr adr' % __name__)
    print('The "sbr/adr" python commands have been installed and are ready for use.')
    print('Usage:')
    print('  sbr <address> [library_name]    # Set breakpoint with ASLR offset')
    print('  adr <address> [library_name]    # Calculate offset from address')
    print('  adr +<offset> [library_name]    # Calculate address from offset')
