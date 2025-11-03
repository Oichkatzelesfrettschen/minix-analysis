# MINIX 3.4.0 x86/IA-32 Core Architectural Files

This document lists key C source (.c), assembly (.S), and header (.h) files within the `sys/arch/i386/` and `minix/kernel/` directories, grouped by their likely architectural purpose. These files are central to understanding MINIX's interaction with the x86/IA-32 CPU.

## 1. Bootstrapping & Initial Setup

These files are involved in the initial boot process, setting up the environment before the main kernel takes over.

*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/boot/biosboot.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/boot/boot2.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/boot/conf.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/boot/devopen.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/boot/devopen.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/bootxx/boot1.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/bootxx/bootxx.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/bootxx/label.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/bootxx/pbr.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/cdboot/cdboot.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/boot_params.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/bootinfo_biosgeom.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/bootinfo_memmap.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/bootinfo.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/bootinfo.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/realprot.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/startprog.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/mbr/gpt.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/mbr/gptmbr.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/mbr/mbr.S`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/head.S`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/pre_init.c`

## 2. CPU & Architecture Specifics (General)

These files define CPU-specific structures, functions, and general architectural constants.

*   `/home/eirikr/Playground/minix/sys/arch/i386/include/cpu.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/cpufunc.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/cputypes.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/cpuvar.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/asm.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/specialreg.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/multiboot.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/cpufunc.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/cpufunc.S`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/arch_system.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/include/arch_proto.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/include/archconst.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/klib.S`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/sconst.h`

## 3. Interrupts & Exceptions

Files related to handling hardware interrupts, software exceptions, and interrupt controllers.

*   `/home/eirikr/Playground/minix/sys/arch/i386/include/intr.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/intrdefs.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/trap.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/i8259.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/apicvar.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/pic.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/exception.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/i8259.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/apic.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/apic.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/apic_asm.S`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/apic_asm.h`
*   `/home/eirikr/Playground/minix/minix/kernel/interrupt.c`
*   `/home/eirikr/Playground/minix/minix/kernel/interrupt.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/include/hw_intr.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/io_intr.S`

## 4. Memory Management

These files handle paging, segmentation, memory protection, and virtual memory.

*   `/home/eirikr/Playground/minix/sys/arch/i386/include/pmap.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/pte.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/vmparam.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/gdt.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/segments.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/memory.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/protect.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/pg_utils.c`
*   `/home/eirikr/Playground/minix/minix/kernel/vm.h`
*   `/home/eirikr/Playground/minix/minix/kernel/system/do_umap.c`
*   `/home/eirikr/Playground/minix/minix/kernel/system/do_umap_remote.c`
*   `/home/eirikr/Playground/minix/minix/kernel/system/do_vmctl.c`
*   `/home/eirikr/Playground/minix/minix/kernel/system/do_vumap.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/arch_do_vmctl.c`

## 5. System Calls & Context Switching

Files related to the interface between user-space and kernel-space, and process context management.

*   `/home/eirikr/Playground/minix/sys/arch/i386/include/mcontext.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/proc.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/tss.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/setjmp.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/mpx.S`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/trampoline.S`
*   `/home/eirikr/Playground/minix/minix/kernel/proc.c`
*   `/home/eirikr/Playground/minix/minix/kernel/proc.h`
*   `/home/eirikr/Playground/minix/minix/kernel/system.c`
*   `/home/eirikr/Playground/minix/minix/kernel/system.h`
*   `/home/eirikr/Playground/minix/minix/kernel/system/do_sigreturn.c`
*   `/home/eirikr/Playground/minix/minix/kernel/system/do_sigsend.c`
*   `/home/eirikr/Playground/minix/minix/kernel/system/do_mcontext.c`
*   `/home/eirikr/Playground/minix/minix/kernel/system/do_exec.c`
*   `/home/eirikr/Playground/minix/minix/kernel/system/do_fork.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/usermapped_data_arch.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/usermapped_glo_ipc.S`

## 6. I/O & Devices

Files related to input/output operations and device interaction.

*   `/home/eirikr/Playground/minix/sys/arch/i386/include/pio.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/pci_machdep.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/isa_machdep.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/isapnp_machdep.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/bios_disk.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/bios_pci.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/biosdisk_ll.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/biosdisk_ll.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/biosdisk.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/biosdisk.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/biospci.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/pcio.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/pcivar.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/io_inb.S`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/io_inl.S`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/io_inw.S`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/io_outb.S`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/io_outl.S`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/io_outw.S`
*   `/home/eirikr/Playground/minix/minix/kernel/system/do_devio.c`
*   `/home/eirikr/Playground/minix/minix/kernel/system/do_sdevio.c`
*   `/home/eirikr/Playground/minix/minix/kernel/system/do_vdevio.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/oxpcie.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/oxpcie.h`

## 7. ACPI & Power Management

Files related to Advanced Configuration and Power Interface.

*   `/home/eirikr/Playground/minix/sys/arch/i386/include/acpi_machdep.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/apmvar.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/acpi.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/acpi.h`

## 8. SMP (Symmetric Multiprocessing)

Files related to managing multiple CPU cores.

*   `/home/eirikr/Playground/minix/sys/arch/i386/include/mpacpi.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/mpbiosreg.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/mpbiosvar.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/mpconfig.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/arch_smp.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/i386/include/arch_smp.h`
*   `/home/eirikr/Playground/minix/minix/kernel/smp.c`
*   `/home/eirikr/Playground/minix/minix/kernel/smp.h`
*   `/home/eirikr/Playground/minix/minix/kernel/cpulocals.c`
*   `/home/eirikr/Playground/minix/minix/kernel/cpulocals.h`
*   `/home/eirikr/Playground/minix/minix/kernel/spinlock.h`

## 9. Miscellaneous Kernel Components

General kernel files that might interact with CPU features or provide core services.

*   `/home/eirikr/Playground/minix/sys/arch/i386/include/clock.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/db_machdep.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/disklabel.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/eisa_machdep.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/elf_machdep.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/endian_machdep.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/endian.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/fenv.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/float.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/frame.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/frameasm.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/freebsd_machdep.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/ibcs2_machdep.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/ieee.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/ieeefp.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/int_const.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/int_fmtio.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/int_limits.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/int_mwgwtypes.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/int_types.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/ipkdb.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/joystick.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/kcore.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/limits.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/loadfile_machdep.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/lock.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/mach_machdep.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/math.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/mca_machdep.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/mtrr.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/mutex.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/param.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/pmc.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/profile.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/psl.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/ptrace.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/rbus_machdep.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/reg.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/return.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/rwlock.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/signal.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/sljit_machdep.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/spkr.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/svr4_machdep.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/sysarch.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/tlog.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/types.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/userret.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/vm86.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/include/wchar_limits.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/biosdelay.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/biosgetrtc.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/biosgetsystime.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/biosmca.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/biosmca.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/biosmem.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/biosmemps2.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/biosmemx.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/biosreboot.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/biosvbe.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/biosvideomode.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/bootmenu.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/bootmenu.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/bootmod.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/comio_direct.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/comio_direct.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/comio.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/conio.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/crt/dos/doscommain.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/crt/dos/start_dos.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/diskbuf.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/diskbuf.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/dos_file.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/dosfile.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/dosfile.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/dump_eax.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/exec.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/gatea20.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/getextmemx.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/getsecs.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/isadma.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/isadmavar.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/isapnp.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/isapnpvar.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/libi386.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/menuutils.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/message.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/message32.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/multiboot.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/netif/3c509.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/netif/3c509.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/netif/3c590.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/netif/3c90xb.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/netif/am7990.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/netif/dp8390.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/netif/dp8390.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/netif/elink3.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/netif/etherdrv.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/netif/i82557.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/netif/lance.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/netif/ne.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/netif/ne.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/netif/netif_small.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/netif/netif_small.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/netif/pcnet_isapnp.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/netif/pcnet_pci.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/netif/wd80x3.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/parseutils.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/pread.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/printmemlist.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/putstr.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/putstr32.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/pvcopy.S`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/rasops.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/test/biosdisk_user.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/test/biosdisk_user.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/test/ether_bpf.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/test/pci_user.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/test/sanamespace.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/test/stand_user.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/vbe.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/lib/vbe.h`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/libsa/getopt.c`
*   `/home/eirikr/Playground/minix/sys/arch/i386/stand/libsa/nfs.c`
*   `/home/eirikr/Playground/minix/minix/kernel/clock.c`
*   `/home/eirikr/Playground/minix/minix/kernel/clock.h`
*   `/home/eirikr/Playground/minix/minix/kernel/config.h`
*   `/home/eirikr/Playground/minix/minix/kernel/const.h`
*   `/home/eirikr/Playground/minix/minix/kernel/debug.c`
*   `/home/eirikr/Playground/minix/minix/kernel/debug.h`
*   `/home/eirikr/Playground/minix/minix/kernel/glo.h`
*   `/home/eirikr/Playground/minix/minix/kernel/ipc.h`
*   `/home/eirikr/Playground/minix/minix/kernel/kernel.h`
*   `/home/eirikr/Playground/minix/minix/kernel/main.c`
*   `/home/eirikr/Playground/minix/minix/kernel/priv.h`
*   `/home/eirikr/Playground/minix/minix/kernel/profile.c`
*   `/home/eirikr/Playground/minix/minix/kernel/profile.h`
*   `/home/eirikr/Playground/minix/minix/kernel/proto.h`
*   `/home/eirikr/Playground/minix/minix/kernel/table.c`
*   `/home/eirikr/Playground/minix/minix/kernel/type.h`
*   `/home/eirikr/Playground/minix/minix/kernel/usermapped_data.c`
*   `/home/eirikr/Playground/minix/minix/kernel/utility.c`
*   `/home/eirikr/Playground/minix/minix/kernel/watchdog.c`
*   `/home/eirikr/Playground/minix/minix/kernel/watchdog.h`

## 10. ARM Architecture (Excluded from i386 audit)

These files are specific to the ARM architecture and are not relevant for the x86/IA-32 audit.

*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/arch_clock.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/arch_do_vmctl.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/arch_reset.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/arch_system.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/bsp/include/bsp_init.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/bsp/include/bsp_intr.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/bsp/include/bsp_padconf.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/bsp/include/bsp_reset.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/bsp/include/bsp_serial.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/bsp/include/bsp_timer.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/bsp/ti/omap_init.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/bsp/ti/omap_intr_registers.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/bsp/ti/omap_intr.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/bsp/ti/omap_padconf.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/bsp/ti/omap_reset.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/bsp/ti/omap_rtc.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/bsp/ti/omap_rtc.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/bsp/ti/omap_serial.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/bsp/ti/omap_serial.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/bsp/ti/omap_timer_registers.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/bsp/ti/omap_timer.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/direct_tty_utils.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/do_padconf.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/exc.S`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/exception.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/glo.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/head.S`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/hw_intr.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/include/arch_clock.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/include/arch_proto.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/include/arch_watchdog.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/include/archconst.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/include/ccnt.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/include/cpufunc.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/include/direct_utils.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/include/hw_intr.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/include/io.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/klib.S`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/memory.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/mpx.S`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/pg_utils.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/phys_copy.S`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/phys_memset.S`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/pre_init.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/protect.c`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/sconst.h`
*   `/home/eirikr/Playground/minix/minix/kernel/arch/earm/timer.h`
