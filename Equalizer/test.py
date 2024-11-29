def plot_spectrogram(self, signal, canvas):
        """
        Plot spectrogram using Matplotlib.
        """
        f, t, Sxx = spectrogram(signal, fs=self.sampling_rate, nperseg=128, noverlap=64)
        canvas.axes.clear()
        
        # Convert power spectral density to decibels
        Sxx_db = 10 * np.log10(Sxx + 1e-10)  # Add small value to avoid log(0)
        print(Sxx.shape)

        if canvas.no_label:
            canvas.no_label = False
            canvas.vmin, canvas.vmax = np.min(Sxx_db), np.max(Sxx_db)

        # Create the spectrogram plot
        cax = canvas.axes.pcolormesh(t, f, Sxx_db, shading='gouraud', cmap='plasma', vmin=canvas.vmin, vmax=canvas.vmax)
        canvas.axes.set_xlabel("Time (s)")
        canvas.axes.set_ylabel("Frequency (Hz)")
        canvas.axes.set_title("Spectrogram")

        # Add a color bar to the plot
        if not hasattr(canvas, 'colorbar') or canvas.colorbar is None:
            print("first plot")
            canvas.colorbar = canvas.figure.colorbar(cax, ax=canvas.axes)
            canvas.colorbar.set_label("Power (dB)")
            
        else:
            print("update")
            # Update the color bar's content
            canvas.colorbar.update_normal(cax)

            # Draw the updated canvas
        canvas.draw()