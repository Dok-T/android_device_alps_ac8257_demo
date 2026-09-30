#!/usr/bin/env python3
"""
apply_twrp_patches.py - patchs source TWRP (bootable/recovery, branche android-12.1) pour le Jancar UJC201

  1. data.cpp : tw_cpu_temp affiche tel quel le texte de TW_CUSTOM_CPU_TEMP_PATH s'il contient "CPU"
     (barre d'etat ecrite par touchfix : temperature + tension d'entree). Sinon comportement d'origine.
  2. Theme landscape_hdpi/ui.xml : en-tete "%tw_cpu_temp%" au lieu de "CPU: %tw_cpu_temp% °C".
  3. Theme common/landscape.xml : entrees Advanced "Power info", "USB: Host mode", "USB: PC mode".

L'ecran (FBIOBLANK) n'a pas besoin de patch source : TW_NO_SCREEN_BLANK + TW_BRIGHTNESS_PATH +
TW_MAX_BRIGHTNESS font ecrire fbdev_blank() dans le fichier de luminosite au lieu de l'ioctl.

Usage : apply_twrp_patches.py <workspace>/bootable/recovery   (idempotent)
"""
import os, sys

MARK = 'UJC201-statustext'

DATA_OLD = '''		value = TWFunc::to_string(convert_temp);
		return 0;
	}
	return -1;
}'''
DATA_NEW = '''#ifdef TW_CUSTOM_CPU_TEMP_PATH
		{
			/* UJC201-statustext : ligne de texte prete a afficher (ecrite par touchfix) */
			string txt;
			if (TWFunc::read_file(EXPAND(TW_CUSTOM_CPU_TEMP_PATH), txt) == 0 && txt.find("CPU") != string::npos) {
				while (!txt.empty() && (txt.back() == '\\n' || txt.back() == '\\r'))
					txt.pop_back();
				value = txt;
				return 0;
			}
		}
#endif
		value = TWFunc::to_string(convert_temp);
		return 0;
	}
	return -1;
}'''
DATA_INIT_OLD = '''	if (TWFunc::Path_Exists(cpu_temp_file)) {
		mConst.SetValue("tw_no_cpu_temp", "0");'''
DATA_INIT_NEW = '''	printf("UJC201-statustext\\n");
	if (TWFunc::Path_Exists(cpu_temp_file)) {
		mConst.SetValue("tw_no_cpu_temp", "0");'''

UI_OLD = '<text>{@cpu_temp=CPU: %tw_cpu_temp% °C}</text>'
UI_NEW = '<text>%tw_cpu_temp%</text>'

ADV_ANCHOR = '''			<listbox style="advanced_listbox">
				<placement x="%center_x%" y="%row2_y%" w="%content_half_width%" h="%fileselector_install_height%"/>
'''
ADV_ITEMS = '''				<listitem name="Power info (Vin / CPU)">
					<action function="cmd">/system/bin/powerinfo</action>
				</listitem>
				<listitem name="USB: Host mode (USB drive)">
					<action function="cmd">/system/bin/usbmode host</action>
				</listitem>
				<listitem name="USB: PC mode (ADB / MTP)">
					<action function="cmd">/system/bin/usbmode device</action>
				</listitem>
'''

def patch(path, old, new, done_marker, count=1):
    s = open(path, encoding='utf-8').read()
    if done_marker in s:
        print('deja applique :', path); return
    n = s.count(old)
    if n < count:
        sys.exit('ERREUR : motif introuvable dans %s (%d/%d)' % (path, n, count))
    s = s.replace(old, new)
    open(path, 'w', encoding='utf-8').write(s)
    print('patche :', path, '(%d)' % n)

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else 'bootable/recovery'
    j = lambda p: os.path.join(root, p)
    patch(j('data.cpp'), DATA_OLD, DATA_NEW, 'UJC201-statustext : ligne')
    patch(j('data.cpp'), DATA_INIT_OLD, DATA_INIT_NEW, 'printf("UJC201-statustext')
    patch(j('gui/theme/landscape_hdpi/ui.xml'), UI_OLD, UI_NEW, UI_NEW, count=1)
    patch(j('gui/theme/common/landscape.xml'), ADV_ANCHOR, ADV_ANCHOR + ADV_ITEMS, 'Power info (Vin / CPU)')

if __name__ == '__main__':
    main()
