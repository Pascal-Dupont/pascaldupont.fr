<div class="wp-block wp-block-kubio-query-layout  position-relative wp-block-kubio-query-layout__outer breevia-index__k__1MCYzfcZN-outer breevia-local-359-outer d-flex h-section-global-spacing align-items-lg-center align-items-md-center align-items-center" data-kubio="kubio/query-layout" id="blog-layout">
	<div class="position-relative wp-block-kubio-query-layout__inner breevia-index__k__1MCYzfcZN-inner breevia-local-359-inner h-section-grid-container h-section-boxed-container">
		<div class="wp-block wp-block-kubio-row  position-relative wp-block-kubio-row__container breevia-index__k__baLWB4dRKjp-container breevia-local-360-container gutters-row-lg-0 gutters-row-v-lg-0 gutters-row-md-0 gutters-row-v-md-1 gutters-row-0 gutters-row-v-0" data-kubio="kubio/row">
			<div class="position-relative wp-block-kubio-row__inner breevia-index__k__baLWB4dRKjp-inner breevia-local-360-inner h-row align-items-lg-stretch align-items-md-stretch align-items-stretch justify-content-lg-center justify-content-md-center justify-content-center gutters-col-lg-0 gutters-col-v-lg-0 gutters-col-md-0 gutters-col-v-md-1 gutters-col-0 gutters-col-v-0">
				<div class="wp-block wp-block-kubio-column  position-relative wp-block-kubio-column__container breevia-index__k__kxeqsSpdy-n-container breevia-local-361-container d-flex h-col-lg h-col-md h-col-auto" data-kubio="kubio/column">
					<div class="position-relative wp-block-kubio-column__inner breevia-index__k__kxeqsSpdy-n-inner breevia-local-361-inner d-flex h-flex-basis h-px-lg-0 v-inner-lg-0 h-px-md-2 v-inner-md-2 h-px-0 v-inner-0">
						<div class="position-relative wp-block-kubio-column__align breevia-index__k__kxeqsSpdy-n-align breevia-local-361-align h-y-container h-column__content h-column__v-align flex-basis-100 align-self-lg-start align-self-md-start align-self-start">
							<div class="wp-block wp-block-kubio-query  position-relative wp-block-kubio-query__container breevia-index__k__CtKC_EuIZL-container breevia-local-362-container" data-kubio="kubio/query">
								<div class="wp-block wp-block-kubio-query-loop  position-relative wp-block-kubio-query-loop__container breevia-index__k__vrf0UGkWrN-container breevia-local-363-container gutters-row-lg-2 gutters-row-v-lg-2 gutters-row-md-0 gutters-row-v-md-2 gutters-row-0 gutters-row-v-2" data-kubio="kubio/query-loop" data-kubio-component="masonry" data-kubio-settings="{&quot;enabled&quot;:&quot;1&quot;,&quot;targetSelector&quot;:&quot;.wp-block-kubio-query-loop__inner&quot;}">
									<div class="position-relative wp-block-kubio-query-loop__inner breevia-index__k__vrf0UGkWrN-inner breevia-local-363-inner h-row">
										<?php breevia_theme()->get('archive-loop')->render(array (
  'view' => 'content/index/loop-item',
)); ?>
									</div>
								</div>
								<?php if(breevia_has_pagination()): ?>
								<div class="wp-block wp-block-kubio-query-pagination  position-relative wp-block-kubio-query-pagination__container breevia-index__k__vD7AVCTELY-container breevia-local-371-container gutters-row-lg-2 gutters-row-v-lg-2 gutters-row-md-0 gutters-row-v-md-2 gutters-row-0 gutters-row-v-2" data-kubio="kubio/query-pagination">
									<div class="position-relative wp-block-kubio-query-pagination__inner breevia-index__k__vD7AVCTELY-inner breevia-local-371-inner h-row align-items-lg-stretch align-items-md-stretch align-items-stretch justify-content-lg-center justify-content-md-center justify-content-center gutters-col-lg-2 gutters-col-v-lg-2 gutters-col-md-0 gutters-col-v-md-2 gutters-col-0 gutters-col-v-2">
										<div class="wp-block wp-block-kubio-column  position-relative wp-block-kubio-column__container breevia-index__k__tBYU0uM8Xx-container breevia-local-372-container d-flex h-col-lg-auto h-col-md-auto h-col-auto" data-kubio="kubio/column">
											<div class="position-relative wp-block-kubio-column__inner breevia-index__k__tBYU0uM8Xx-inner breevia-local-372-inner d-flex h-flex-basis h-px-lg-0 v-inner-lg-2 h-px-md-0 v-inner-md-2 h-px-0 v-inner-2">
												<div class="position-relative wp-block-kubio-column__align breevia-index__k__tBYU0uM8Xx-align breevia-local-372-align h-y-container h-column__content h-column__v-align flex-basis-auto align-self-lg-center align-self-md-center align-self-center">
													<?php if(breevia_has_pagination_button(true)): ?>
													<div class="position-relative wp-block-kubio-pagination-nav-button__spacing breevia-index__k__ELgmeRXRD--spacing breevia-local-373-spacing">
														<span class="wp-block wp-block-kubio-pagination-nav-button  position-relative wp-block-kubio-pagination-nav-button__outer breevia-index__k__ELgmeRXRD--outer breevia-local-373-outer kubio-button-container" data-kubio="kubio/pagination-nav-button">
															<a class="position-relative wp-block-kubio-pagination-nav-button__link breevia-index__k__ELgmeRXRD--link breevia-local-373-link h-w-100 h-global-transition" href="<?php breevia_get_navigation_button_link(true); ?>">
																<span class="position-relative wp-block-kubio-pagination-nav-button__text breevia-index__k__ELgmeRXRD--text breevia-local-373-text kubio-inherit-typography">
																	<?php esc_html_e('Previous', 'breevia'); ?>
																</span>
															</a>
														</span>
													</div>
													<?php endif; ?>
												</div>
											</div>
										</div>
										<div class="wp-block wp-block-kubio-column  position-relative wp-block-kubio-column__container breevia-index__k__P2OarhUKUK-container breevia-local-374-container d-flex h-col-lg h-col-md h-col" data-kubio="kubio/column">
											<div class="position-relative wp-block-kubio-column__inner breevia-index__k__P2OarhUKUK-inner breevia-local-374-inner d-flex h-flex-basis h-px-lg-2 v-inner-lg-2 h-px-md-2 v-inner-md-2 h-px-1 v-inner-2">
												<div class="position-relative wp-block-kubio-column__align breevia-index__k__P2OarhUKUK-align breevia-local-374-align h-y-container h-column__content h-column__v-align flex-basis-100 align-self-lg-center align-self-md-center align-self-center">
													<div class="wp-block wp-block-kubio-pagination-numbers  position-relative wp-block-kubio-pagination-numbers__outer breevia-index__k__tRiQFlrj8q-outer breevia-local-375-outer" data-kubio="kubio/pagination-numbers">
														<?php breevia_pagination_numbers(); ?>
													</div>
												</div>
											</div>
										</div>
										<div class="wp-block wp-block-kubio-column  position-relative wp-block-kubio-column__container breevia-index__k__2nd5yuWmz9-container breevia-local-376-container d-flex h-col-lg-auto h-col-md-auto h-col-auto" data-kubio="kubio/column">
											<div class="position-relative wp-block-kubio-column__inner breevia-index__k__2nd5yuWmz9-inner breevia-local-376-inner d-flex h-flex-basis h-px-lg-0 v-inner-lg-2 h-px-md-0 v-inner-md-2 h-px-0 v-inner-2">
												<div class="position-relative wp-block-kubio-column__align breevia-index__k__2nd5yuWmz9-align breevia-local-376-align h-y-container h-column__content h-column__v-align flex-basis-auto align-self-lg-center align-self-md-center align-self-center">
													<?php if(breevia_has_pagination_button()): ?>
													<div class="position-relative wp-block-kubio-pagination-nav-button__spacing breevia-index__k__zv2xsom5z-spacing breevia-local-377-spacing">
														<span class="wp-block wp-block-kubio-pagination-nav-button  position-relative wp-block-kubio-pagination-nav-button__outer breevia-index__k__zv2xsom5z-outer breevia-local-377-outer kubio-button-container" data-kubio="kubio/pagination-nav-button">
															<a class="position-relative wp-block-kubio-pagination-nav-button__link breevia-index__k__zv2xsom5z-link breevia-local-377-link h-w-100 h-global-transition" href="<?php breevia_get_navigation_button_link(); ?>">
																<span class="position-relative wp-block-kubio-pagination-nav-button__text breevia-index__k__zv2xsom5z-text breevia-local-377-text kubio-inherit-typography">
																	<?php esc_html_e('Next', 'breevia'); ?>
																</span>
															</a>
														</span>
													</div>
													<?php endif; ?>
												</div>
											</div>
										</div>
									</div>
								</div>
								<?php endif; ?>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>
