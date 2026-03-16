import numpy as np
from pypeit.images.buildimage import TiltImage, ArcImage
from pypeit.spectrographs.util import load_spectrograph
from pypeit.par.pypeitpar import WavelengthSolutionPar, WaveTiltsPar
from pypeit.wavecalib import BuildWaveCalib

def make_wavecalib_pypeit(data: np.ndarray,
                          slits,
                          spectrograph_name: str = 'keck_lris_red',
                          lamps: list[str] = None,
                          method: str = 'holy-grail',
                          sigdetect: float = 10.0,  # Detection threshold for line finding
                          n_first: int = 2,
                          n_final: int = 6
                          ):
    """
    Create a PyPEIT wavelength calibration object from an arc lamp image and slit traces.

    Args:
        data: arc lamp image
        slits: PypeIT slit trace object (from tracing step)
        spectrograph_name: PyPEIT spectrograph name (default: keck_lris_red)
            Use keck_lris_red or keck_lris_blue as proxy for LRIS2 evaluation
        method: Method for wavelength solution (default: 'holy-grail')
        sigdetect: Detection threshold for line finding (default: 10.0)
        n_first: Order of fitting to use as first guess (default: 2)
        n_final: Final order of fitting (default: 6)
    """
    # Load spectrograph
    spectrograph = load_spectrograph(spectrograph_name)

    # Create ArcImage from the input data
    arc_image = ArcImage(data.astype(np.float64), detector=spectrograph.get_detector_par(1))

    # Build WavelengthSolutionPar with LRIS default settings (can be customized as needed)
    wave_par = WavelengthSolutionPar()
    wave_par["lamps"] = lamps if lamps else ["HgI", "NeI", "ArI", "ZnI", "CdI"]
    wave_par["method"] = method
    wave_par['reid_arxiv'] = 'keck_lris_blue_B1200_3400_d560_ArCdHgNeZn.fits' if "blue" in spectrograph_name \
                                else 'keck_lris_red_R900_5500_ArCdHgNeZn.fits'
    wave_par["sigdetect"] = sigdetect
    wave_par["rms_thresh_frac_fwhm"] = 0.06
    wave_par["n_first"] = n_first
    wave_par["n_final"] = n_final

    waveCalib = BuildWaveCalib(arc_image, slits, spectrograph, wave_par, lamps=wave_par["lamps"])
    wv_calib = waveCalib.run(skip_QA=True)
    return wv_calib