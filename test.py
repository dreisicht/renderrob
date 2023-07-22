import sys
sys.path.append('C:/Users/peter/Documents/repositories/RenderRob')
import render_settings_setter
rss = render_settings_setter.RenderSettingsSetter('', [''])
rss.activate_addons([])
rss.set_camera('')
rss.set_render_settings(render_device='0', border=True,
                        samples='', motion_blur=False, engine='cycles')
rss.set_denoising_settings(an_denoise=False, denoise=False)
rss.set_output_settings(frame_step=1, xres='', yres='', percres=100)
