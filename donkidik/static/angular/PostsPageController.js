// controller
(function(){
	angular.module('donkidik')
		.controller('HomeController', function($scope, postService){

			$scope.posts = [];
			$scope.spots = [];
			$scope.create_post_type = ''
			$scope.selected_post_type = 'general';
			$scope.new_post_error = '';

			$scope.get_range = function(min, max){
				var ret = [];
				for (var i=min; i<=max; i++)
					ret.push(i);
				return ret;
			};

			$scope.get_posts = function(uid){
				$scope.posts = [];
				postService.get_posts(uid).then(function(res){
					if (res.success) {
						$scope.posts = res.posts;
						$scope.posts_loaded = true;
					}
					else {
						//TODO: replace loading with error message
						alert('Error getting posts...');
					}
				});
			};


			$scope.get_spots = function(){
				$scope.spots = [];
				var err = false;
				postService.get_spots().then(function(res){
					if (res.success) {
						if (res.spots){
							$scope.spots = res.spots;
						}
						else{
							err = true;
						}
					}
					else {
						err = true;
					}
					if (err){
						//TODO: tell user there was a problem reaching server
						alert("Error getting spots")
					}
				});
			};

			$scope.reload_post_comments = function(post) {
				postService.reload_post_comments(post.post_id).then(function(res){
					if (res.success) {
						post.comments = res.comments;
					}
					else {
						alert('Error reloading post comments');
					}
				});
			};

			$scope.post_comment = function(post){
				if (!post.comm_text)
					return;

				var txt = post.comm_text;
				postService.post_comment(post.post_id, txt).then(function(){
					$scope.reload_post_comments(post);
					post.comm_text = '';
				});
			};

			$scope.delete_post = function(post){
				
				if (!confirm('Sure?'))
					return;

				postService.delete_post(post.post_id).then(function(res){
					if (res.success) {
						for (var i=0; i<$scope.posts.length; i++) {
							if ($scope.posts[i].post_id == post.post_id) {
								$scope.posts.splice(i, 1);
								break;
							}
						}
					}
					else {
						alert('Error deleting post');
					}
				});
			};

			// NEW
				$scope.submit_new_post = function(){

					$scope.new_post_error = '';
					var post_type = $scope.selected_post_type,
						text = $scope.new_post_text;

					if (!text) {
						$scope.new_post_error = 'Please enter your message';
						return;
					}

				var data = {
					post_type: (post_type == 'general' ? 1 : 2),
					text: text
				};

				if ($scope.selected_post_type == 'report') {
					var spot_id = ($scope.new_post_spot ? $scope.new_post_spot.id : false),
						knots = $scope.new_post_knots;
					if (!spot_id) {
						$scope.new_post_error = '<p>Please choose a Spot</p>';
					}
					if (!knots) {
						$scope.new_post_error += '<p>Please choose knots</p>';
					}
					if ($scope.new_post_error)
						return;
					
					data.spot_id = spot_id;
					data.knots = knots;
				}

				postService.create_post(data).then(function(res){
					if (res.success) {
						$scope.new_post_text = '';
						$scope.new_post_error = '';
						$scope.new_post_knots = '';
						$scope.new_post_spot = '';
						$scope.posts.unshift(res.post);
					}
					else {
						$scope.new_post_error = 'Error saving post: ' + res.error || 'Internal error';
					}
				});

			};

			$scope.post_upvote = function(post,uid){
				postService.post_upvote(post.post_id).then(function(res){
					if (res.status=='OK'){
						post.score += res.change_score;
						post.author.score = Math.max(post.author.score+res.change_score,0)
						if (res.change_score == -1){ // was previously upvoted. cancel the upvote
							post.is_upvoted = false;
							var i = post.upvotes.indexOf(res.uid);
							if (i >-1) post.upvotes.splice(i,1); //was already upvoted. cancel the previous upvote
							else alert('mismatch between post.upvotes and res.change_score');
							//TODO: remove else clause
						}
						else{ //increase score
							if (res.change_score > 1){
								var i = post.downvotes.indexOf(res.uid);
								if (i >-1){
									post.downvotes.splice(i,1); // delete previous downvote
									post.is_downvoted = false;
								}
								else alert('mismatch between post.downvotes and res.change_score');
								//TODO: remove else clause
							}
							post.upvotes.push(res.uid)
							post.is_upvoted = true;
						}
					}
					else{
						// TODO communicate this to UI
						if (res.error) alert(res.error);
						else alert("Service failed!");
					}
				});
			};

			$scope.post_downvote = function(post){
				postService.post_downvote(post.post_id).then(function(res){
					if (res.status=='OK'){
						post.score += res.change_score;
						post.author.score = Math.max(post.author.score+res.change_score,0)
						if (res.change_score == 1){ // was previously downvoted. cancel the downvote
							post.is_downvoted = false;
							var i = post.downvotes.indexOf(res.uid);
							if (i >-1) post.downvotes.splice(i,1); //was already downvoted. cancel the previous downvote
							else alert('mismatch between post.downvotes and res.change_score');
							//TODO: remove else clause
						}
						else{ //reduced score
							if (res.change_score < -1){
								var i = post.upvotes.indexOf(res.uid);
								if (i >-1){
									post.upvotes.splice(i,1); // delete previous upvote
									post.is_upvoted = false;
								}
								else alert('mismatch between post.upotes and res.change_score');
								//TODO: remove else clause
							}
							post.downvotes.push(res.uid)
							post.is_downvoted = true;
						}
					}
					else{
						// TODO communicate this to UI
						if (res.error) alert(res.error);
						else alert("Service failed!");
					}
				});
			};
			$scope.get_spots();
			$scope.get_posts(null);

		});

})();